import os
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum
from .models import House, UserProfile, AcceptedChallenge, FitnessActivity, HouseActivity, HouseChallenge, HouseBadge, UserBadge, check_and_award_badges, ActivityFeedItem, Notification, FriendRequest, Friendship, Team, TeamMembership, Comment, Reaction
from .forms import FitnessActivityForm
from fitness.utils.agent_logic import recommend_workout, generate_coachbot_feedback, calculate_streak, client
from fitness.utils.octocoach import ensure_houses_exist, get_octocoach_message_for_user, get_real_house_list
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
import json
from django.utils.timezone import now
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from datetime import date
from django.contrib.auth.models import User
from django.db import models
from fitness.models import House

@csrf_exempt
@require_POST
@login_required
def save_onboarding(request):
    profile = request.user.userprofile
    try:
        data = json.loads(request.body)
        profile.onboarding_answers = data
        profile.onboarding_complete = True
        profile.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

# Configure logging with more detail
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Create your views here.
from django.shortcuts import render

def octofit_home(request):
    ensure_houses_exist()  # Make sure all four houses exist before login/registration
    houses = House.objects.all()
    onboarding_needed = False
    octocoach_message = None
    if request.user.is_authenticated:
        onboarding_needed = not getattr(request.user.userprofile, 'onboarding_complete', False)
        # Always get the latest OctoCoach message for this user (no session cache)
        octocoach_message = get_octocoach_message_for_user(request.user)
    context = {
        'houses': houses,
        'onboarding_needed': onboarding_needed,
        'octocoach_message': octocoach_message,
        # ...other context if needed...
    }
    return render(request, "home.html", context)

def leaderboard(request):
    houses = House.objects.all().order_by('-points')
    house_scores = list(houses.values('name', 'points'))
    prediction = ""
    if len(houses) > 1:
        top_house = houses[0]
        second_house = houses[1]
        diff = top_house.points - second_house.points
        if diff <= 20:
            prediction = f"🏁 If {second_house.name} logs 2 more workouts, they’ll take the lead!"
    context = {
        'houses': houses,
        'house_scores': house_scores,
        'prediction': prediction,
    }
    return render(request, 'leaderboard.html', context)

@login_required
def house_detail(request, name):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    if not user_profile.house:
        return render(request, "house_detail.html", {
            "house_name": None,
            "no_house": True,
            "user": user,
        })
    house = House.objects.filter(name__iexact=name).first()
    if not house:
        return render(request, "404.html", {"message": "House not found"}, status=404)
    if house.points in [100, 1000]:
        return render(request, "house_detail.html", {"house_name": house.name, "show_confetti": True, "house": house})
    if house.points >= 500 and not house.confetti_shown:
        house.confetti_shown = True
        house.save()
        show_confetti = True
    else:
        show_confetti = False

    # User progress and leaderboard
    user_activities = FitnessActivity.objects.filter(user=user)
    from django.utils import timezone
    from datetime import timedelta
    start_of_week = timezone.now().date() - timedelta(days=timezone.now().weekday())
    user_workouts_this_week = user_activities.filter(date__gte=start_of_week).count()
    user_streak = calculate_streak(user)
    user_house_points = user_profile.house.points if user_profile.house else 0
    house_members = UserProfile.objects.filter(house=house).select_related('user')
    leaderboard = sorted([
        {'username': m.user.username, 'points': FitnessActivity.objects.filter(user=m.user).count()} for m in house_members
    ], key=lambda x: x['points'], reverse=True)[:10]
    import random
    quotes = [
        "Push yourself, because no one else is going to do it for you!",
        "Success is not for the lazy.",
        "Every rep brings you closer to your goal!",
        "Don’t be afraid to fail. Be afraid not to try.",
        "You got this! Let’s make today legendary!",
        "Strength does not come from winning. Your struggles develop your strengths."
    ]
    motivational_quote = random.choice(quotes)
    workouts_progress_percent = min(100, int((user_workouts_this_week / 3) * 100)) if user_workouts_this_week else 0
    streak_progress_percent = min(100, int((user_streak / 7) * 100)) if user_streak else 0
    house_points_progress_percent = min(100, int((user_house_points / 500) * 100)) if user_house_points else 0

    # Fetch house data from DB
    mascot = house.mascot
    color = house.color
    theme = house.theme or house.name
    description = house.description
    activities = list(house.activities.values_list('description', flat=True))
    challenges = list(house.challenges.values_list('description', flat=True))
    badges = list(house.badges.all())
    # User badge progress
    user_badge_ids = set(UserBadge.objects.filter(user=user, badge__in=badges).values_list('badge_id', flat=True))

    # Rewards system
    from .models import Reward, UserReward
    all_rewards = list(Reward.objects.all())
    unlocked_reward_ids = set(UserReward.objects.filter(user=user).values_list('reward_id', flat=True))

    # Challenge progress for this user and house
    accepted = set(AcceptedChallenge.objects.filter(user=request.user, challenge_description__in=challenges).values_list('challenge_description', flat=True))
    completed = set(AcceptedChallenge.objects.filter(user=request.user, challenge_description__in=challenges, completed_at__isnull=False).values_list('challenge_description', flat=True))
    challenge_progress = {
        'accepted': accepted,
        'completed': completed,
        'total': len(challenges),
        'done': len(completed),
    }
    # Calculate challenge progress percent for the progress bar
    if len(challenges) > 0:
        challenge_progress_percent = int((len(completed) / len(challenges)) * 100)
    else:
        challenge_progress_percent = 0

    # Build challenge display list for template (fixes template error)
    challenges_display = []
    for challenge in challenges:
        challenges_display.append({
            'text': challenge,
            'is_accepted': challenge in accepted,
            'is_completed': challenge in completed,
        })

    return render(request, "house_detail.html", {
        "house_name": house.name,
        "show_confetti": show_confetti,
        "house": house,
        "user_workouts_this_week": user_workouts_this_week,
        "user_streak": user_streak,
        "user_house_points": user_house_points,
        "house_members": leaderboard,
        "motivational_quote": motivational_quote,
        "workouts_progress_percent": workouts_progress_percent,
        "streak_progress_percent": streak_progress_percent,
        "house_points_progress_percent": house_points_progress_percent,
        "activities": activities,
        "challenges": challenges_display,
        "house_theme": theme,
        "mascot": mascot,
        "color": color,
        "house_description": description,
        "badges": badges,
        "user_badge_ids": user_badge_ids,
        "challenge_progress": challenge_progress,
        "challenge_progress_percent": challenge_progress_percent,
        "rewards": all_rewards,
        "unlocked_reward_ids": unlocked_reward_ids,
        "no_house": False,
    })

@login_required
def submit_activity(request):
    if request.method == 'POST':
        form = FitnessActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.user = request.user
            activity.save()
            # Award 10 points
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.house:
                user_profile.house.points += 10
                user_profile.house.save()
            # Prepare updated progress
            from django.utils import timezone
            from datetime import timedelta
            start_of_week = timezone.now().date() - timedelta(days=timezone.now().weekday())
            workouts_this_week = FitnessActivity.objects.filter(user=request.user, date__gte=start_of_week).count()
            streak = calculate_streak(request.user)
            house_points = user_profile.house.points if user_profile.house else 0
            # AJAX: return JSON for frontend update
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Activity submitted! You earned 10 points.',
                    'workouts_this_week': workouts_this_week,
                    'streak': streak,
                    'house_points': house_points
                })
            # Fallback: render page
            recommendations = recommend_workout(activity.user)
            feedback = generate_coachbot_feedback(activity.user)
            return render(request, 'submit_activity.html', {'form': form, 'recommendations': recommendations, 'feedback': feedback})
    else:
        form = FitnessActivityForm()
    return render(request, 'submit_activity.html', {'form': form})

@login_required
def octocoach_response(request):
    if request.method == "POST":
        user_input = request.POST.get("message", "")
        
        # 🧠 Dynamic system prompt with your vibe
        persona = getattr(request.user.userprofile, 'bot_persona', 'arnold')
        if persona == 'arnold':
            system_prompt = (
                "You are Classic Arnold Schwarzenegger: a bold, energetic, and funny fitness coach. "
                "Use Arnold's catchphrases, humor, and lots of motivation. Respond in a direct, playful way with gym slang and encouragement."
            )
            avatar = '💪'
        elif persona == 'jennifer':
            system_prompt = (
                "You are Jennifer Aniston: a friendly, supportive, and wellness-focused coach. "
                "Give gentle, positive advice with a touch of Hollywood charm."
            )
            avatar = '🌟'
        elif persona == 'katy':
            system_prompt = (
                "You are Katy Perry: a pop-star coach who is energetic, colorful, and fun. "
                "Use pop culture references, song lyrics, and lots of encouragement."
            )
            avatar = '🎤'
        elif persona == 'mel':
            system_prompt = (
                "You are Mel Gibson: a tough, action-movie style coach. "
                "Give bold, dramatic, and inspiring advice, like a movie hero rallying the troops."
            )
            avatar = '🦸'
        else:
            system_prompt = (
                "You are OctoCoach 🐙, a motivating, emoji-loving fitness coach. "
                "You help users balance workouts, maintain streaks, and complete challenges. "
                "Respond in a friendly, concise way with occasional emojis and encouragement."
            )
            avatar = '🐙'
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )
            reply = response.choices[0].message.content
            return JsonResponse({"response": reply, "avatar": avatar})
        except Exception as e:
            logger.error(f"Error in octocoach_response: {str(e)}")
            return JsonResponse({"error": "Oops! Something went wrong 🤖"}, status=500)

@csrf_exempt
def accept_challenge(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You must be logged in to accept a challenge.'}, status=401)
    if request.method == 'POST':
        data = json.loads(request.body)
        description = data.get('description')
        xp = int(data.get('xp', 10))
        # Prevent duplicate acceptances
        obj, created = AcceptedChallenge.objects.get_or_create(
            user=request.user,
            challenge_description=description,
            defaults={'xp_points': xp}
        )
        if not created:
            return JsonResponse({'message': 'Already accepted', 'accepted': True})
        # Fetch challenges from DB
        house = request.user.userprofile.house
        if house:
            challenges = list(house.challenges.values_list('description', flat=True))
        else:
            challenges = []
        accepted = list(AcceptedChallenge.objects.filter(user=request.user, challenge_description__in=challenges).values_list('challenge_description', flat=True))
        completed = list(AcceptedChallenge.objects.filter(user=request.user, challenge_description__in=challenges, completed_at__isnull=False).values_list('challenge_description', flat=True))
        return JsonResponse({
            'message': 'Challenge accepted!',
            'accepted': accepted,
            'completed': completed,
            'total': len(challenges),
            'done': len(completed),
            'xp': xp
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
@login_required
def complete_challenge(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)
    data = json.loads(request.body)
    description = data.get('description')
    xp = int(data.get('xp', 10))
    challenge = AcceptedChallenge.objects.filter(user=request.user, challenge_description=description, completed_at__isnull=True).first()
    if not challenge:
        return JsonResponse({'error': 'Challenge not found or already completed.'}, status=404)
    challenge.completed_at = now()
    challenge.xp_points = xp  # Optionally update XP if needed
    challenge.save()
    # Optionally, add XP to user profile or house points here
    # Award badges after challenge completion
    check_and_award_badges(request.user)
    # Award rewards after challenge completion
    from .models import check_and_award_rewards
    check_and_award_rewards(request.user)
    # Fetch challenges from DB
    house = request.user.userprofile.house
    if house:
        challenges = list(house.challenges.values_list('description', flat=True))
    else:
        challenges = []
    accepted = list(AcceptedChallenge.objects.filter(user=request.user, challenge_description__in=challenges).values_list('challenge_description', flat=True))
    completed = list(AcceptedChallenge.objects.filter(user=request.user, challenge_description__in=challenges, completed_at__isnull=False).values_list('challenge_description', flat=True))
    return JsonResponse({
        'message': 'Challenge completed! XP awarded.',
        'accepted': accepted,
        'completed': completed,
        'total': len(challenges),
        'done': len(completed),
        'xp': xp
    })

@csrf_exempt
def ask_coachbot(request):
    if request.method == 'POST':
        try:
            from fitness.utils.agent_logic import client
            if client is None:
                logger.error("OpenAI client is not initialized. Check your API key and OpenAI package version.")
                return JsonResponse({"error": "OpenAI client is not configured. Please check your API key and package version."}, status=500)

            data = json.loads(request.body)
            user_input = data.get('message', '').strip()
            if not user_input:
                return JsonResponse({"error": "Message cannot be empty."}, status=400)

            # Strict intercept for house-related questions
            house_keywords = ['house list', 'what house', 'which house', 'houses', 'pick a house', 'choose a house']
            if any(k in user_input.lower() for k in house_keywords):
                houses = get_real_house_list()
                msg = "Here are your real house options in OctoFit:\n"
                for h in houses:
                    msg += f"\n🏠 {h['name']}: {h['description']} (Theme: {h['theme']}, Mascot: {h['mascot']})"
                msg += "\nPick the one that matches your vibe!"
                return JsonResponse({"response": msg})

            # ...existing user state logic...
            if request.user.is_authenticated:
                user = request.user
                streak_count = calculate_streak(user) or 0
                last_activity = FitnessActivity.objects.filter(user=user).order_by('-created_at').first()
                last_activity_str = (
                    f"{last_activity.activity_type} on {last_activity.created_at.strftime('%Y-%m-%d')}"
                    if last_activity else "No activities yet"
                )
                house_name = user.userprofile.house.name if user.userprofile.house else "No house assigned"
                house_standing = "Top 3"  # Example placeholder
                # Inject real house list into system prompt
                houses = get_real_house_list()
                house_list_str = "\n".join([
                    f"- {h['name']}: {h['description']} (Theme: {h['theme']}, Mascot: {h['mascot']})" for h in houses
                ])
            else:
                streak_count = 0
                last_activity_str = "No activities yet"
                house_name = "No house assigned"
                house_standing = "Unknown"
                house_list_str = "- Kraken\n- Montana\n- Razor\n- Serene"

            # Construct the system message and user context
            system_message = (
                "You are OctoCoach, a motivating fitness assistant in the OctoFit app. "
                f"The user's real username is '{user.username}'. "
                "You must only reference the following real houses and their details, never inventing new ones.\n"
                f"HOUSES:\n{house_list_str}\n"
                "Your job is to help users stay active by recommending workouts, giving feedback on streaks, "
                "and celebrating milestones. Be friendly, energetic, and creative! Always use the user's real username in your responses."
            )
            user_context = (
                f"{user_input} (User is in House: {house_name}, Streak: {streak_count} days, "
                f"Last activity: {last_activity_str}, House standing: {house_standing}, Username: {user.username})"
            )

            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_context}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                coachbot_response = response.choices[0].message.content.strip()
                logger.info(f"Successfully generated response for chat bot user")
                return JsonResponse({"response": coachbot_response}, status=200)
            except Exception as e:
                logger.error(f"OpenAI API error: {str(e)}")
                return JsonResponse(
                    {"error": "Coachbot is currently unavailable. Please try again later."},
                    status=500
                )
        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return JsonResponse({"error": "Invalid request format"}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error in ask_coachbot: {str(e)}")
            return JsonResponse(
                {"error": "An unexpected error occurred. Please contact support."},
                status=500
            )
    return JsonResponse({"error": "Invalid request method."}, status=400)

@login_required
@csrf_exempt
def upload_progress_photo(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        photo = request.FILES['photo']
        user = request.user
        # Save to MEDIA_ROOT/progress_photos/<username>/YYYYMMDD_<filename>
        from datetime import datetime
        today = datetime.now().strftime('%Y%m%d')
        user_folder = f'progress_photos/{user.username}/'
        filename = f'{today}_{photo.name}'
        file_path = user_folder + filename
        saved_path = default_storage.save(file_path, ContentFile(photo.read()))
        # Optionally, store the path in the user's profile or a new model
        return JsonResponse({'success': True, 'url': default_storage.url(saved_path)})
    return JsonResponse({'success': False, 'error': 'No photo uploaded.'}, status=400)

@login_required
@csrf_exempt
def list_progress_photos(request):
    user = request.user
    user_folder = f'progress_photos/{user.username}/'
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    photo_urls = []
    if media_root:
        abs_folder = os.path.join(media_root, user_folder)
        if os.path.exists(abs_folder):
            for fname in os.listdir(abs_folder):
                if fname.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                    photo_urls.append(settings.MEDIA_URL + user_folder + fname)
    return JsonResponse({'photos': photo_urls})

@login_required
def protected_view(request):
    # Example protected view
    return render(request, 'fitness/protected.html')

@login_required
@require_GET
def daily_tip(request):
    profile = request.user.userprofile
    today = date.today()
    if profile.last_tip_date == today and profile.last_tip_text:
        return JsonResponse({"tip": profile.last_tip_text, "date": str(today)})
    # Generate a new tip using OpenAI
    try:
        streak = profile.streak_count
        house = profile.house.name if profile.house else "No house"
        prompt = (
            f"You are OctoCoach, a motivating fitness coach for students. "
            f"Give a short, friendly, actionable fitness or wellness tip for today. "
            f"Personalize it for a user in the '{house}' house with a {streak}-day streak. "
            f"Add an emoji and keep it under 140 characters."
        )
        from fitness.utils.agent_logic import client
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=60,
            temperature=0.8
        )
        tip = response.choices[0].message.content.strip()
    except Exception:
        tip = "Stay active and have fun today! 💪"
    profile.last_tip_date = today
    profile.last_tip_text = tip
    profile.save()
    return JsonResponse({"tip": tip, "date": str(today)})

@login_required
@require_POST
@csrf_exempt
def save_checklist_state(request):
    # Save checklist state in user profile (or a new model/field)
    state = request.POST.get('state')
    if not state:
        return JsonResponse({'error': 'No state provided'}, status=400)
    profile = request.user.userprofile
    profile.checklist_state = state
    profile.save()
    return JsonResponse({'success': True})

@login_required
@csrf_exempt
def get_checklist_state(request):
    profile = request.user.userprofile
    return JsonResponse({'state': getattr(profile, 'checklist_state', None)})

@login_required
@require_GET
def user_progress_api(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    from django.utils import timezone
    from datetime import timedelta
    start_of_week = timezone.now().date() - timedelta(days=timezone.now().weekday())
    workouts_this_week = FitnessActivity.objects.filter(user=user, date__gte=start_of_week).count()
    streak = calculate_streak(user)
    house_points = user_profile.house.points if user_profile.house else 0
    workouts_progress_percent = min(100, int((workouts_this_week / 3) * 100)) if workouts_this_week else 0
    streak_progress_percent = min(100, int((streak / 7) * 100)) if streak else 0
    house_points_progress_percent = min(100, int((house_points / 500) * 100)) if house_points else 0
    return JsonResponse({
        'workouts_this_week': workouts_this_week,
        'streak': streak,
        'house_points': house_points,
        'workouts_progress_percent': workouts_progress_percent,
        'streak_progress_percent': streak_progress_percent,
        'house_points_progress_percent': house_points_progress_percent,
    })

@login_required
@require_GET
def activity_feed(request):
    profile = request.user.userprofile
    house = profile.house
    feed = ActivityFeedItem.objects.filter(house=house).order_by('-created_at')[:30]
    items = [
        {
            'user': item.user.username,
            'action': item.action,
            'description': item.description,
            'target_user': item.target_user.username if item.target_user else None,
            'created_at': item.created_at.isoformat()
        } for item in feed
    ]
    return JsonResponse({'feed': items})

@login_required
@require_GET
def notifications_api(request):
    notifs = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:20]
    items = [
        {'id': n.id, 'message': n.message, 'type': n.notif_type, 'created_at': n.created_at.isoformat()} for n in notifs
    ]
    return JsonResponse({'notifications': items})

@login_required
@require_POST
def mark_notifications_read(request):
    ids = request.POST.getlist('ids[]')
    Notification.objects.filter(user=request.user, id__in=ids).update(is_read=True)
    return JsonResponse({'success': True})

@login_required
@require_GET
def user_profile_api(request):
    profile = request.user.userprofile
    data = {
        'username': request.user.username,
        'avatar': profile.avatar,
        'bio': profile.bio,
        'interests': profile.interests,
        'house': profile.house.name if profile.house else None,
        'email_reminders': profile.email_reminders,
    }
    return JsonResponse({'profile': data})

@login_required
@require_POST
def update_profile_api(request):
    profile = request.user.userprofile
    data = json.loads(request.body)
    profile.avatar = data.get('avatar', profile.avatar)
    profile.bio = data.get('bio', profile.bio)
    profile.interests = data.get('interests', profile.interests)
    if 'email_reminders' in data:
        profile.email_reminders = bool(data['email_reminders'])
    profile.save()
    return JsonResponse({'success': True})

@login_required
@require_GET
def analytics_api(request):
    from django.utils import timezone
    from datetime import timedelta
    user = request.user
    today = timezone.now().date()
    # Last 14 days activity
    days = [(today - timedelta(days=i)) for i in range(13, -1, -1)]
    activity_counts = [
        FitnessActivity.objects.filter(user=user, date=day).count() for day in days
    ]
    streak = calculate_streak(user)
    # House performance (last 14 days)
    house = user.userprofile.house
    house_points = []
    if house:
        for day in days:
            points = FitnessActivity.objects.filter(user__userprofile__house=house, date=day).count()
            house_points.append(points)
    else:
        house_points = [0]*14
    return JsonResponse({
        'dates': [d.isoformat() for d in days],
        'activity_counts': activity_counts,
        'streak': streak,
        'house_points': house_points
    })

@login_required
@require_POST
@csrf_exempt
def send_friend_request(request):
    data = json.loads(request.body)
    to_user_id = data.get('to_user_id')
    if not to_user_id or int(to_user_id) == request.user.id:
        return JsonResponse({'error': 'Invalid user.'}, status=400)
    to_user = User.objects.filter(id=to_user_id).first()
    if not to_user:
        return JsonResponse({'error': 'User not found.'}, status=404)
    req, created = FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
    if not created:
        return JsonResponse({'error': 'Request already sent.'}, status=400)
    return JsonResponse({'success': True})

@login_required
@require_POST
@csrf_exempt
def respond_friend_request(request):
    data = json.loads(request.body)
    req_id = data.get('request_id')
    action = data.get('action')  # 'accept' or 'decline'
    req = FriendRequest.objects.filter(id=req_id, to_user=request.user).first()
    if not req:
        return JsonResponse({'error': 'Request not found.'}, status=404)
    if action == 'accept':
        req.status = 'accepted'
        req.save()
        Friendship.objects.get_or_create(user1=min(req.from_user, req.to_user, key=lambda u: u.id), user2=max(req.from_user, req.to_user, key=lambda u: u.id))
        Notification.objects.create(user=req.from_user, message=f"{request.user.username} accepted your friend request!", notif_type='friend')
    else:
        req.status = 'declined'
        req.save()
    return JsonResponse({'success': True})

@login_required
@require_GET
def list_friends(request):
    user = request.user
    friends = Friendship.objects.filter(models.Q(user1=user) | models.Q(user2=user))
    friend_ids = [f.user2.id if f.user1 == user else f.user1.id for f in friends]
    friend_users = User.objects.filter(id__in=friend_ids)
    data = [{'id': u.id, 'username': u.username} for u in friend_users]
    return JsonResponse({'friends': data})

@login_required
@require_POST
@csrf_exempt
def create_team(request):
    data = json.loads(request.body)
    name = data.get('name')
    if not name:
        return JsonResponse({'error': 'Team name required.'}, status=400)
    team = Team.objects.create(name=name, created_by=request.user)
    TeamMembership.objects.create(team=team, user=request.user)
    return JsonResponse({'success': True, 'team_id': team.id})

@login_required
@require_POST
@csrf_exempt
def join_team(request):
    data = json.loads(request.body)
    team_id = data.get('team_id')
    team = Team.objects.filter(id=team_id).first()
    if not team:
        return JsonResponse({'error': 'Team not found.'}, status=404)
    TeamMembership.objects.get_or_create(team=team, user=request.user)
    return JsonResponse({'success': True})

@login_required
@require_GET
def list_teams(request):
    teams = TeamMembership.objects.filter(user=request.user).select_related('team')
    data = [{'id': m.team.id, 'name': m.team.name} for m in teams]
    return JsonResponse({'teams': data})

@login_required
@require_POST
@csrf_exempt
def post_comment(request):
    data = json.loads(request.body)
    activity_id = data.get('activity_id')
    photo_url = data.get('photo_url')
    text = data.get('text')
    if not text:
        return JsonResponse({'error': 'Comment required.'}, status=400)
    comment = Comment.objects.create(user=request.user, activity_id=activity_id, photo_url=photo_url, text=text)
    # Optionally, notify the activity/photo owner
    if activity_id:
        act = ActivityFeedItem.objects.filter(id=activity_id).first()
        if act and act.user != request.user:
            Notification.objects.create(user=act.user, message=f"{request.user.username} commented on your activity!", notif_type='comment')
    return JsonResponse({'success': True, 'comment_id': comment.id})

@login_required
@require_GET
def list_comments(request):
    activity_id = request.GET.get('activity_id')
    photo_url = request.GET.get('photo_url')
    comments = Comment.objects.filter(activity_id=activity_id) if activity_id else Comment.objects.filter(photo_url=photo_url)
    data = [{'id': c.id, 'user': c.user.username, 'text': c.text, 'created_at': c.created_at.isoformat()} for c in comments.order_by('created_at')]
    return JsonResponse({'comments': data})

@login_required
@require_POST
@csrf_exempt
def post_reaction(request):
    data = json.loads(request.body)
    activity_id = data.get('activity_id')
    photo_url = data.get('photo_url')
    emoji = data.get('emoji')
    if not emoji:
        return JsonResponse({'error': 'Emoji required.'}, status=400)
    reaction, created = Reaction.objects.get_or_create(user=request.user, activity_id=activity_id, photo_url=photo_url, emoji=emoji)
    # Optionally, notify the activity/photo owner
    if activity_id:
        act = ActivityFeedItem.objects.filter(id=activity_id).first()
        if act and act.user != request.user:
            Notification.objects.create(user=act.user, message=f"{request.user.username} reacted to your activity!", notif_type='reaction')
    return JsonResponse({'success': True})

@login_required
@require_GET
def list_reactions(request):
    activity_id = request.GET.get('activity_id')
    photo_url = request.GET.get('photo_url')
    reactions = Reaction.objects.filter(activity_id=activity_id) if activity_id else Reaction.objects.filter(photo_url=photo_url)
    data = [{'user': r.user.username, 'emoji': r.emoji, 'created_at': r.created_at.isoformat()} for r in reactions.order_by('created_at')]
    return JsonResponse({'reactions': data})

@login_required
def push_notification_poll(request):
    """
    API endpoint for polling new challenges or achievements for push notifications.
    Returns the latest unseen challenge or achievement for the user.
    """
    user = request.user
    # Example: get the latest challenge and achievement for the user
    # You may want to customize this logic for your app's real data
    from .models import AcceptedChallenge, UserBadge
    latest_challenge = (
        AcceptedChallenge.objects.filter(user=user, completed_at__isnull=False)
        .order_by('-completed_at').first()
    )
    latest_achievement = (
        UserBadge.objects.filter(user=user)
        .order_by('-awarded_at').first()
    )
    data = {}
    if latest_challenge:
        data['new_challenge'] = {
            'id': latest_challenge.id,
            'text': latest_challenge.challenge_description,
        }
    if latest_achievement:
        data['new_achievement'] = {
            'id': latest_achievement.id,
            'text': latest_achievement.badge.name if latest_achievement.badge else 'Achievement unlocked!',
        }
    return JsonResponse(data)

from django.views.decorators.http import require_POST
from .models import ChallengeSuggestion, House

@login_required
@require_POST
def suggest_challenge(request):
    desc = request.POST.get('description', '').strip()
    house_id = request.POST.get('house_id')
    if not desc or not house_id:
        return JsonResponse({'success': False, 'error': 'Description and house required.'}, status=400)
    house = House.objects.filter(id=house_id).first()
    if not house:
        return JsonResponse({'success': False, 'error': 'House not found.'}, status=404)
    ChallengeSuggestion.objects.create(user=request.user, house=house, description=desc)
    return JsonResponse({'success': True, 'message': 'Suggestion submitted for review!'})

@require_POST
@login_required
def join_house(request):
    house_id = request.POST.get('house_id')
    if not house_id:
        return redirect('home')
    try:
        house = House.objects.get(id=house_id)
        profile = request.user.userprofile
        from django.utils import timezone
        profile.house_joined_at = timezone.now()
        profile.house = house
        profile.save()
    except House.DoesNotExist:
        pass
    return redirect('home')

def fitness_home(request):
    return HttpResponse("<h2>Fitness Home</h2><p>Welcome to the fitness section. Try /submit-activity/ or /accept-challenge/.</p>")

