# OctoFit Agent Behavior Documentation

## Overview
OctoFit is enhanced with smart, gamified, and visually engaging features powered by modular agents. These agents act as mini-assistants to improve user engagement and provide personalized fitness experiences.

## Agents

### 1. 🔁 Streak Detector Agent
**Purpose**: Tracks user activity streaks and rewards users for consistency.

- **Behavior**:
  - Detects how many consecutive days a user has logged fitness activities.
  - Rewards users with badges or points for achieving streak milestones (e.g., 5-day streak).
  - Triggers confetti or pop-ups to celebrate milestones.

- **Implementation**:
  - Tracks streaks using the `calculate_streak` function in `utils/agent_logic.py`.
  - Updates streak count in the `UserProfile` model.
  - Displays streak information on the dashboard.

### 2. 🧠 Smart Workout Recommender
**Purpose**: Provides personalized workout recommendations to users.

- **Behavior**:
  - Suggests a different type of workout for balance.
  - Recommends challenges to try.
  - Suggests house-boosting activities if the user's house is behind in points.

- **Implementation**:
  - Generates recommendations using the `recommend_workout` function in `utils/agent_logic.py`.
  - Logs recommendations in the `RecommendationLog` model.
  - Displays recommendations dynamically in the `submit_activity.html` template.

### 3. 📅 Challenge Suggestion Bot
**Purpose**: Suggests daily/weekly challenges to users.

- **Behavior**:
  - Recommends challenges based on popular activities.
  - Highlights low-participation categories to balance scoring.

- **Implementation**:
  - Integrated into the `recommend_workout` function.
  - Displays challenges in the dashboard and activity submission pages.

### 4. 🤖 OctoCoach Assistant
**Purpose**: Acts as a chatbot-like assistant to guide users.

- **Behavior**:
  - Answers user queries about streaks, recommendations, and challenges.
  - Provides dynamic responses based on user data.
  - Plays audio clips of Arnold Schwarzenegger's iconic phrases for motivation.

- **Implementation**:
  - Frontend: Chat panel in `base.html` with dynamic responses and audio integration.
  - Backend: `octocoach_response` view in `views.py` to handle user queries.

## Visual Enhancements
- Emojis/icons are used to make recommendations visually engaging.
- Confetti effects celebrate user achievements.
- Arnold Schwarzenegger's image and audio clips add personality to OctoCoach.

## Future Enhancements
- Add more dynamic responses to OctoCoach.
- Introduce AI-based recommendations for workouts and challenges.
- Expand gamification features with leaderboards and team-based competitions.

## Conclusion
The agents in OctoFit work together to create a fun, engaging, and personalized fitness experience. They encourage users to stay active, participate in challenges, and contribute to their house's success.