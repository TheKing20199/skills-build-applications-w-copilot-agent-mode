# 🏆 OctoFit Challenge League: Hogwarts Meets Peloton, Powered by AI Agents

> _“Don’t wait for tomorrow. Start your fitness journey today with OctoFit. If you want to be a champion, you have to train like one. And with AI on your team, you’ll be back… stronger than ever!”_  
> — Arnold (probably)

---

## 🚀 What is OctoFit?
OctoFit is the world’s first AI-powered, house-based fitness league for schools, teams, and hackathons. Imagine Hogwarts houses, Peloton energy, and a GPT-4 agent as your personal coach—gamified, social, and accessible for everyone.

- **Compete in themed houses:** Kraken, Montana, Rayzor, Serene—each with unique challenges and badges.
- **AI Agent at the Core:** OctoCoach (GPT-4) guides, motivates, and celebrates you at every step.
- **Real-time feedback:** Streaks, badges, and house battles update instantly.
- **For Schools, Teams, and Hackathons:** Use in PE class, corporate step challenges, or as a showcase of modern AI agent orchestration.

---

## 🎬 Demo Flow (Impress the Judges!)
1. **Guest Walkthrough:** Click “Try as Guest” for instant access—no signup needed.
2. **AI Onboarding:** Take the “Which Sea Creature Are You?” GPT-powered quiz to get sorted into a house.
3. **Log Activities:** Submit a workout and get a personalized coaching prompt from OctoCoach.
4. **Take on Challenges:** Complete a challenge and see instant AI feedback and confetti.
5. **Notifications:** Click the bell to see real-time updates for friend requests, comments, and more.
6. **Leaderboard & House Battle:** Watch the animated house battle meter and see who’s on top.
7. **Admin Power:** Use Django admin to add/edit houses, challenges, and badges—no code required.

---

## 🤖 Why It’s a True AI Agent Demo
- **GPT-4 Agent Logic:**
  - Assigns houses via personality quiz
  - Guides onboarding with personalized journey advice
  - Gives context-aware coaching after every activity/challenge
  - Powers daily tips, chat, and milestone celebrations
- **Agent is Proactive:** Triggers on user actions, not just on demand
- **All logic is documented and testable**

---

## 🧠 Architecture
- Django backend (fitness, accounts, admin)
- OpenAI API (OctoCoach agent, daily tips, onboarding, feedback)
- Social & gamification modules (friends, teams, comments, notifications)
- Responsive, accessible frontend

---

## 🏅 Real-World Use Cases
- **Schools:** Gamify PE, boost engagement, and foster teamwork
- **Teams/Companies:** Run step challenges, wellness battles, and more
- **Hackathons:** Show off agent orchestration, real-time feedback, and AI-powered UX

---

## 🦾 How to Run Locally
1. `pip install -r requirements.txt`
2. Add your OpenAI API key to `.env`
3. `python manage.py migrate && python manage.py populate_db`
4. `python manage.py runserver`
5. Open your browser and get moving!

---

## 📸 Screenshots & Demo Video
- ![OctoFit Dashboard](docs/octofitapp-small.png)
- [Add your demo video link here]

---

## 🏆 Why OctoFit Will Turn Heads
- **It’s Hogwarts meets Peloton, with a real AI agent.**
- **Instant demo mode for judges—no setup, no friction.**
- **Every user action gets a smart, motivating AI response.**
- **Beautiful, accessible, and admin-friendly.**
- **All code is clean, documented, and ready for production or the classroom.**

---

## 📜 License
MIT

---

_Ready to win? Fork, run, and let OctoCoach guide you to victory!_
