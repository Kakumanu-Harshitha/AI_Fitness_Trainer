# AI Fitness Tracker — Computer Vision Coaching with ML Personalization

AI‑powered fitness tracking that delivers real‑time workout analysis, posture correction, and personalized coaching using computer vision and intelligent models — no GPU required.

---

## 📌 Project Overview

- Problem: Manual rep counting, poor posture awareness, and generic plans reduce workout effectiveness at home.
- Solution: Hybrid system combining MediaPipe Pose, explainable state machines, a Random‑Forest model for personalization, and an LLM coach for context‑aware guidance.
- Impact: Accurate tracking, tailored calorie/water/intensity guidance, and actionable plans — all on commodity hardware and the web.

---

## 🚀 Key Innovations

- GPU‑free pipeline: Real‑time performance via MediaPipe + deterministic logic + lightweight ML
- Hybrid system: Integrates Computer Vision, Machine Learning, and LLM reasoning
- Explainable AI: State machines for interpretable reps and posture validation
- Real‑time UX: Low‑latency predictions and coaching

---

## ✨ Features

- Real‑time pose detection and overlay
- Rep counting and posture analysis
- ML‑based personalization (calories, water, intensity)
- AI chatbot coaching with strict, UI‑friendly formatting
- Dashboard analytics and streaks
- Gamification (XP, levels, badges, leaderboard)
- Real‑time chat via WebSockets
- Voice feedback hooks

---

## 🧩 Tech Stack

- Frontend: React, Tailwind CSS, MediaPipe (browser)
- Backend: FastAPI, PostgreSQL, SQLAlchemy (Async), WebSockets
- AI/ML: MediaPipe, scikit‑learn RandomForestRegressor, joblib, LLM coach

---

## 🧭 How It Works (High‑Level)

1. User starts a workout in the web app  
2. MediaPipe detects landmarks in the browser  
3. State machines convert motion into reps, timers, and posture scores  
4. Events and summaries persist to the database  
5. Personalization yields calories, water, and intensity targets  
6. Chatbot composes a concise plan using predictions + user profile  

📖 For detailed system architecture, see [architecture.md](./architecture.md)

---

## ⚙️ Setup

Backend
1. `cd backend`
2. Create env and install requirements  
   - Windows: `python -m venv .venv && .venv\\Scripts\\activate`  
   - `pip install -r requirements.txt`
3. Configure `.env` (database URL, JWT secret, etc.)
4. Run migrations: `alembic upgrade head`
5. Start: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

Frontend
1. `cd frontend`
2. `npm install`
3. Create `.env` with `REACT_APP_API_URL=http://localhost:8000`
4. `npm start`

---

## 🗂 Project Structure

```
Ai_Fitness_Tracker/
├── backend/
│   ├── app/
│   │   ├── api/v1/        # FastAPI routers (auth, dashboard, routines, ai, chatbot)
│   │   ├── core/          # settings, security, middleware
│   │   ├── core_ai/       # pose, state machines, personalization, coach
│   │   ├── db/            # models, async sessions
│   │   └── services/      # business logic
│   ├── scripts/           # utilities and migrations
└── frontend/
    ├── public/
    └── src/
        ├── components/
        ├── contexts/
        ├── screens/       # HomeDashboard, LiveWorkout, Stats
        └── utils/         # API config
```

---

## 🔮 Future Improvements

- Multi‑agent coaching (form, motivation, pacing, recovery)
- RL‑based progression for adaptive difficulty
- On‑device lightweight models for temporal form analysis
- Federated learning for privacy‑preserving personalization
- Native mobile with shared CV core

---

## License

MIT — see LICENSE for details.
