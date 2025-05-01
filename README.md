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
1. **Register/Login:** Create an account or log in with your credentials.
2. **AI Onboarding:** Take the “Which Sea Creature Are You?” GPT-powered quiz to get sorted into a house.
3. **Log Activities:** Submit a workout and get a personalized coaching prompt from OctoCoach.
4. **Take on Challenges:** Complete a challenge and see instant AI feedback and confetti.
5. **Profile Settings:** Update your info and toggle email reminders (with a clear Save and success message).
6. **House Stats:** Click the House Stats link to see your house’s progress and leaderboard.
7. **Notifications:** Click the bell to see real-time updates for friend requests, comments, and more.
8. **Leaderboard & House Battle:** Watch the animated house battle meter and see who’s on top.
9. **Admin Power:** Use Django admin to add/edit houses, challenges, and badges—no code required.

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

## ⚡ Quick Start (Linux)

1. **Install requirements:**
   ```bash
   pip install -r octofit-tracker/backend/requirements.txt
   ```
2. **Add your OpenAI API key to `.env` in `octofit-tracker/backend/`**
3. **Migrate and seed demo data:**
   ```bash
   cd octofit-tracker/backend
   python3 manage.py migrate
   python3 manage.py populate_db
   ```
4. **Start the server:**
   ```bash
   pkill -f runserver; sleep 1; cd /workspaces/skills-build-applications-w-copilot-agent-mode/octofit-tracker/backend && python3 manage.py runserver
   ```
5. **Open your browser at** [http://localhost:8000/](http://localhost:8000/)

---

## 🗺️ How to Navigate OctoFit
- **Home:** See all houses, join/switch, and view your dashboard.
- **Login/Register:** Use the login or register links to create an account and access all features.
- **Profile Settings:** Click your username/avatar in the navbar to access your profile and update your info, avatar, and email reminders.
- **Onboarding:** New users are guided by OctoCoach and the personality quiz.
- **Log Activity:** Use the “Log Activity” button on the home or house page.
- **Challenges:** Accept and complete challenges from your house page.
- **House Stats:** Click the "House Stats" link in the navbar to view your house's stats and leaderboard (links to your house if assigned).
- **Notifications:** Click the bell in the navbar for real-time updates (friend requests, comments, etc.).
- **Friends/Teams:** Use the navbar links to connect and compete.
- **Admin:** Go to `/admin/` to manage houses, challenges, and badges (superuser required).

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
