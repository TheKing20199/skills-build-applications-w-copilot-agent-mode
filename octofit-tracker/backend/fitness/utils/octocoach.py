import random
from datetime import datetime, timedelta
from django.utils import timezone
from fitness.models import UserProfile, House, OctoCoachChatHistory

HOUSE_NAMES = ["Kraken", "Montana", "Razor", "Serene"]

FUN_FACTS = [
    "Did you know? Consistency beats intensity. Keep showing up!",
    "Tip: Try a new activity this week for bonus points!",
    "OctoCoach says: Hydrate and celebrate your wins!",
    "Fun fact: The Kraken house mascot is inspired by legendary sea creatures!",
    "Serene house members are known for their calm and focus."
]

MILESTONE_MESSAGES = {
    3: "You're on a 3-day streak! Keep it up for a badge!",
    5: "5 activities logged! You're crushing it!",
    7: "7-day streak! You earned a badge and a confetti shower!",
    100: "100 house points! Your house is proud!"
}

def get_real_house_list():
    houses = House.objects.all()
    return [
        {
            'name': h.name,
            'mascot': h.mascot,
            'theme': h.theme,
            'description': h.description,
            'color': h.color
        } for h in houses
    ]

def get_random_arnold_quote():
    return random.choice([
        "Hasta la vista, {username}! Ready to crush your streak today?",
        "Get to the chopper, {username}! Time to move! 🏋️‍♂️",
        "You can do it, {username}! No pain, no gain! 💪",
        "Stay hungry, {username}, stay fit!",
        "It’s not a tumor, it’s just your growing muscles, {username}!",
        "Strength does not come from winning. Your struggles develop your strengths, {username}.",
        "Come with me if you want to lift!"
    ])

def get_guest_greeting(persona):
    login_url = "/accounts/login/"
    register_url = "/register/"
    if persona == 'arnold':
        return (f"Ahoy there, future OctoFitter! 🐙 Before we pump any iron, you gotta hop aboard. ⛵ <a href='{login_url}'>Log in</a> or <a href='{register_url}'>create an account</a> — I’ll be here cheering you on! 💪 Once you’re in, I’ll help you pick a house, log activities, and start your fitness adventure! 🌊")
    elif persona == 'jennifer':
        return (f"Hey there, future OctoFitter! 🌟 Before we get started, please <a href='{login_url}'>log in</a> or <a href='{register_url}'>create an account</a>. I’ll be here cheering you on! ✨ Once you’re in, I’ll help you pick a house, log activities, and start your wellness journey!")
    elif persona == 'katy':
        return (f"Hey superstar! 🎤 Before we make fitness fireworks, <a href='{login_url}'>log in</a> or <a href='{register_url}'>create an account</a> — I’ll be here cheering you on! 💃🌈 Once you’re in, I’ll help you pick a house, log activities, and start your fitness adventure!")
    elif persona == 'mel':
        return (f"Ready for action, recruit? 🦸‍♂️ Before you join the OctoFit squad, <a href='{login_url}'>log in</a> or <a href='{register_url}'>create an account</a>. I’ll be here cheering you on! ⚔️💥 Once you’re in, I’ll help you pick a house, log activities, and start your fitness adventure!")
    else:
        return (f"Ahoy there, future OctoFitter! 🐙 Before we swim any laps, you’ll need to hop aboard. ⛵ — I’ll be here cheering you on! 💪 Once you’re in, I’ll help you pick a house, log activities, and start your fitness adventure! 🌊")

def get_octocoach_message_for_user(user, user_input=None, event=None, persona=None):
    if not user.is_authenticated:
        persona = persona or 'arnold'
        return get_guest_greeting(persona)
    profile = user.userprofile
    now = timezone.now()
    # Retrieve last bot message from history
    last_bot_msg = OctoCoachChatHistory.objects.filter(user=user, sender='bot').order_by('-timestamp').first()
    # Personalized greeting only if not greeted in last 24h
    if not last_bot_msg or (now - last_bot_msg.timestamp).total_seconds() > 86400:
        greeting = f"👋 Hey {user.username}! Welcome back to OctoFit. You're in House {profile.house.name if profile.house else 'None'}. Ready to crush your goals today?"
        OctoCoachChatHistory.objects.create(user=user, sender='bot', message=greeting, context_type='greeting')
        return greeting
    # House switch event
    if event == 'house_switch':
        msg = f"🏠 You just switched to House {profile.house.name}! Let's earn some points and unlock new badges!"
        OctoCoachChatHistory.objects.create(user=user, sender='bot', message=msg, context_type='house_switch')
        return msg
    # Activity log event
    if event == 'activity_log':
        msg = f"💪 Nice job logging your activity! Keep it up for more streaks and rewards. Want to try a new challenge?"
        OctoCoachChatHistory.objects.create(user=user, sender='bot', message=msg, context_type='activity_log')
        return msg
    # Milestone event
    if event == 'milestone':
        msg = f"🎉 Congrats {user.username}! You hit a new milestone. Check your badges and celebrate!"
        OctoCoachChatHistory.objects.create(user=user, sender='bot', message=msg, context_type='milestone')
        return msg
    # FAQ/Knowledge base for app-specific help
    faq = {
        'log activity': "To log an activity, click the 'Log Activity' button at the top of the page. You can record your workout, and it will count toward your streak and house points!",
        'how do i log': "Just click the 'Log Activity' button at the top of the home or house page to record your workout!",
        'earn badge': "You earn badges by completing challenges, maintaining streaks, and reaching house milestones. Check the House Badges section for your progress!",
        'switch house': "You can switch houses anytime from the home or house page by clicking the 'Switch House' button.",
        'join house': "To join a house, go to the home page and click 'Switch to' on your favorite house!",
        'challenge': "House challenges are listed on your house page. Accept and complete them to earn XP and badges!",
        'photo': "Upload your progress photos from the dashboard to celebrate your journey!",
        'leaderboard': "The leaderboard shows the top members in your house. Log activities to climb the ranks!",
        'progress': "Your dashboard and house page show your real-time progress, streaks, and house points!",
        'house list': None,  # handled below
        'what house': None,  # handled below
        'which house': None,  # handled below
    }
    if user_input:
        lower = user_input.lower()
        # Intercept house-related questions and answer with real house data
        if any(key in lower for key in ['house list', 'what house', 'which house', 'houses', 'pick a house', 'choose a house']):
            houses = get_real_house_list()
            msg = "Here are your real house options in OctoFit:\n"
            for h in houses:
                msg += f"\n🏠 {h['name']}: {h['description']} (Theme: {h['theme']}, Mascot: {h['mascot']})"
            msg += "\nPick the one that matches your vibe!"
            OctoCoachChatHistory.objects.create(user=user, sender='bot', message=msg, context_type='house_list')
            return msg
        for key, answer in faq.items():
            if key in lower and answer:
                OctoCoachChatHistory.objects.create(user=user, sender='bot', message=answer, context_type='faq')
                return answer
    # Show onboarding only if user has NOT joined a house
    if not profile.house:
        return "Welcome to OctoFit! I'm OctoCoach. Let's get you started—join a house to begin your journey!"
    # If user is in a house, greet with house-specific message and a random Arnold-ism or motivational quote
    if profile.house:
        quote = get_random_arnold_quote().format(username=user.username)
        return f"🐙 {quote} You're in House {profile.house.name}. Ready to log an activity or take on a new challenge?"
    # House assignment
    if profile.house and not profile.house_joined_at:
        return f"Nice! You just joined House {profile.house.name}! Ready to log your first workout?"
    # First activity
    if profile.first_activity_logged_at and (not profile.last_octocoach_message or profile.first_activity_logged_at > profile.last_octocoach_message):
        return "Awesome, you logged your first workout! Keep going!"
    # Milestones
    for streak, msg in sorted(MILESTONE_MESSAGES.items()):
        if profile.streak_count >= streak and (not profile.last_streak_milestone or profile.last_streak_milestone < streak):
            profile.last_streak_milestone = streak
            profile.save()
            return msg
    # Skipped steps
    if not profile.house:
        return "Oops! Looks like you skipped the house assignment. Let’s go back and fix that. Choose your house: Kraken, Montana, Razor, or Serene."
    # Inactivity
    if profile.first_activity_logged_at and (now - profile.first_activity_logged_at).days > 3:
        return "Haven't seen you log an activity in a while! Let's get moving—your house is counting on you!"
    # Occasional fun fact
    if random.random() < 0.1:
        return random.choice(FUN_FACTS)
    return None

def ensure_houses_exist():
    for name in HOUSE_NAMES:
        House.objects.get_or_create(name=name, defaults={
            'mascot': name + ' Mascot',
            'color': '#cccccc',
            'description': f'{name} house',
            'theme': name
        })
