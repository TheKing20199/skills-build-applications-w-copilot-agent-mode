from dotenv import load_dotenv
load_dotenv()
import os
from datetime import timedelta
from django.utils.timezone import now
import logging
from openai import OpenAI
from .cache_utils import get_cached_response, cache_response

# Debugging statement
print('DEBUG: OPENAI_API_KEY at agent_logic.py import:', os.getenv('OPENAI_API_KEY'))

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables and initialize OpenAI client
try:
    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        organization=os.getenv('OPENAI_ORGANIZATION_ID')
    )
    logger.info("OpenAI client initialized in agent_logic.py")
except Exception as e:
    logger.error(f"Error initializing OpenAI client in agent_logic: {str(e)}")
    client = None

def calculate_streak(user):
    """
    Calculate the current streak of consecutive days a user has logged activities.

    Args:
        user (User): The user for whom to calculate the streak.

    Returns:
        int: The number of consecutive days the user has logged activities.
    """
    from fitness.models import FitnessActivity  # Import locally to avoid circular import
    activities = FitnessActivity.objects.filter(user=user).order_by('-date')
    if not activities:
        return 0

    streak = 1
    previous_date = activities[0].date

    for activity in activities[1:]:
        if previous_date - activity.date == timedelta(days=1):
            streak += 1
            previous_date = activity.date
        else:
            break

    return streak

def recommend_workout(user):
    """
    Generate personalized workout recommendations using OpenAI.

    Args:
        user (User): The user for whom to generate recommendations.

    Returns:
        dict: A dictionary containing AI-generated recommendations.
    """
    from fitness.models import FitnessActivity, RecommendationLog

    try:
        # Get user's workout history
        recent_activities = FitnessActivity.objects.filter(user=user).order_by('-date')[:5]
        activity_history = [f"{a.activity_type} on {a.date.strftime('%Y-%m-%d')}" for a in recent_activities]
        
        if client:
            system_prompt = (
                "You are OctoCoach's recommendation engine. Generate three specific, actionable workout "
                "recommendations based on the user's recent activity history. Focus on variety, progression, "
                "and maintaining streaks. Keep each recommendation under 100 characters."
            )

            user_context = (
                f"User has done: {', '.join(activity_history) if activity_history else 'No recent activities'}. "
                f"Current streak: {calculate_streak(user)} days."
            )

            # Check cache first
            cached_recommendations = get_cached_response(user_context, 'workout_recommendations')
            if cached_recommendations:
                logger.info(f"Using cached recommendations for user {user.username}")
                return cached_recommendations

            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_context}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                
                ai_recommendations = response.choices[0].message.content.strip().split('\n')
                recommendations = {
                    "balance": ai_recommendations[0] if len(ai_recommendations) > 0 else "Try mixing up your routine!",
                    "challenge": ai_recommendations[1] if len(ai_recommendations) > 1 else "Join a new challenge!",
                    "house_boost": ai_recommendations[2] if len(ai_recommendations) > 2 else "Log a workout to boost house points!"
                }
                
                # Cache the recommendations
                cache_response(user_context, 'workout_recommendations', recommendations)
                logger.info(f"Generated and cached AI recommendations for user {user.username}")
            except Exception as e:
                logger.error(f"Error generating AI recommendations: {str(e)}")
                recommendations = get_fallback_recommendations(recent_activities)
        else:
            recommendations = get_fallback_recommendations(recent_activities)

        # Log recommendations
        for rec_type, message in recommendations.items():
            RecommendationLog.objects.create(user=user, recommendation_type=rec_type)

        return recommendations

    except Exception as e:
        logger.error(f"Error in recommend_workout: {str(e)}")
        return get_fallback_recommendations([])

def get_fallback_recommendations(activities):
    """Fallback recommendations when AI is unavailable."""
    if not activities:
        return {
            "balance": "Start your fitness journey with a simple walk! 🚶‍♂️",
            "challenge": "Try our beginner-friendly challenge this week! 🎯",
            "house_boost": "Any activity helps your house earn points! 🏆"
        }
    
    last_activity = activities[0] if activities else None
    if last_activity and last_activity.activity_type == "Cardio":
        return {
            "balance": "Time for some strength training! 💪",
            "challenge": "Can you do 10 push-ups today? 💪",
            "house_boost": "A HIIT session would boost your house points! 🔥"
        }
    return {
        "balance": "How about some cardio today? 🏃‍♂️",
        "challenge": "Try a new workout type this week! 🌟",
        "house_boost": "Your house needs your energy! 🏋️‍♂️"
    }

def generate_coachbot_feedback(user):
    """
    Generate personalized AI feedback based on user's activity patterns.

    Args:
        user (User): The user for whom to generate feedback.

    Returns:
        str: AI-generated personalized feedback message.
    """
    from fitness.models import FitnessActivity
    
    try:
        recent_activities = FitnessActivity.objects.filter(user=user).order_by('-date')[:3]
        streak = calculate_streak(user)
        
        if client:
            activity_summary = [f"{a.activity_type} on {a.date.strftime('%Y-%m-%d')}" for a in recent_activities]
            
            system_prompt = (
                "You are OctoCoach, a motivating fitness assistant. Generate a short, encouraging feedback "
                "message (max 150 characters) based on the user's recent activities and streak. Use emojis "
                "and be energetic but concise!"
            )

            user_context = (
                f"Recent activities: {', '.join(activity_summary) if activity_summary else 'No recent activities'}. "
                f"Current streak: {streak} days."
            )

            # Check cache first
            cached_feedback = get_cached_response(user_context, 'feedback')
            if cached_feedback:
                logger.info(f"Using cached feedback for user {user.username}")
                return cached_feedback

            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_context}
                    ],
                    max_tokens=100,
                    temperature=0.7
                )
                
                feedback = response.choices[0].message.content.strip()
                
                # Cache the feedback
                cache_response(user_context, 'feedback', feedback)
                logger.info(f"Generated and cached AI feedback for user {user.username}")
                return feedback
            except Exception as e:
                logger.error(f"Error generating AI feedback: {str(e)}")
                return get_fallback_feedback(recent_activities, streak)
        else:
            return get_fallback_feedback(recent_activities, streak)

    except Exception as e:
        logger.error(f"Error in generate_coachbot_feedback: {str(e)}")
        return "Keep up the great work! 💪"

def get_fallback_feedback(activities, streak):
    """Generate fallback feedback when AI is unavailable."""
    if not activities:
        return "Welcome to OctoFit! Ready to start your fitness journey? 🚀"
    
    if streak > 5:
        return f"Amazing {streak}-day streak! You're on fire! 🔥"
    elif streak > 0:
        return f"Nice {streak}-day streak! Keep it going! 💪"
    
    last_activity = activities[0] if activities else None
    if last_activity:
        if last_activity.activity_type == "Cardio":
            return "Great cardio session! How about some strength training next? 💪"
        elif last_activity.activity_type == "Strength Training":
            return "Crushing those weights! Maybe try some yoga for recovery? 🧘‍♂️"
        else:
            return "Way to mix up your routine! Keep that variety coming! 🌟"
    
    return "Every workout counts! What will you try today? 💪"