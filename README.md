# 🏋️ AI Fitness Tracker

An intelligent, computer vision-based fitness application designed to analyze human body movements in real-time, providing automated workout tracking, posture analysis, and AI-driven coaching.

## 📌 Project Overview
The **AI Fitness Tracker** solves the problem of manual workout logging and lack of posture feedback during home workouts. By leveraging MediaPipe's pose estimation, the app automatically counts repetitions for dynamic exercises (like squats and pushups) and tracks duration for static poses (like planks).

### Key Highlights:
- **AI Pose Detection**: Real-time body landmark tracking.
- **Automatic Rep Counting**: Intelligent state machines to detect completed reps.
- **Form Analysis**: Real-time posture scoring and corrective feedback.
- **Time-based Exercises**: Automatic timer that resets if the pose is broken.
- **End-to-End Tracking**: Full workout history, stats, and personal bests.

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: React (JavaScript)
- **Styling**: Tailwind CSS
- **Computer Vision**: MediaPipe Pose (Original JS Library)
- **Icons**: Lucide React
- **State Management**: React Context API

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (Primary) / SQLite (Development Fallback)
- **ORM**: SQLAlchemy (Async)
- **Authentication**: JWT (JSON Web Tokens)
- **Real-time**: WebSockets for live notifications and chat.

---

## ✨ Features

- **🔐 Secure Authentication**: JWT-based signup and login system.
- **📊 Interactive Dashboard**: Overview of weekly activity, calories burned, and total workouts.
- **💪 Real-time Workout Tracking**:
    - **Dynamic Rep Counting**: Squats, Push-ups, Lunges.
    - **Static Pose Tracking**: Plank, Tree Pose, Chair Pose.
- **🏆 Gamification**: Leaderboard system to compete with friends, levels, and XP.
- **📈 Performance Health**: Automated calculation of Recovery Rate and Joint Stress.
- **💬 Internal Chat**: Connect with friends via a real-time WebSocket-based chat system.
- **🎤 Voice Feedback**: AI Coach providing motivational and corrective advice during sets.

---

## 📁 Folder Structure

The repository contains two main modules:

```text
Ai_Fitness_Tracker/
├── backend/            # FastAPI Backend
│   ├── app/            # Application core logic
│   │   ├── api/        # API Endpoints (v1)
│   │   ├── core/       # Security, Config, and Middleware
│   │   ├── core_ai/    # AI Pose Analysis & State Machines
│   │   ├── db/         # Models and Database connections
│   │   └── services/   # Business logic
│   └── scripts/        # Database migration & utility scripts
└── frontend/           # React Web Application
    ├── public/         # Static assets
    └── src/            # React Source code
        ├── components/ # Reusable UI components
        ├── contexts/   # State management
        ├── screens/    # App pages (LiveWorkout, Stats, etc.)
        └── utils/      # AI Engines & API config
```

> **Note**: Folders like `mobile/` and `web/` are used for local development/experimentation and are not included in this repository.

---

## 🚀 Setup Instructions

### 1. Backend Setup (FastAPI)

1. **Navigate to backend folder**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the `backend/` directory (see [Environment Variables](#environment-variables) section below).

5. **Run Migrations**:
   ```bash
   alembic upgrade head
   ```

6. **Start the server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

### 2. Frontend Setup (React)

1. **Navigate to frontend folder**:
   ```bash
   cd frontend
   ```

2. **Install npm packages**:
   ```bash
   npm install
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the `frontend/` directory.

4. **Start the application**:
   ```bash
   npm start
   ```

---

## 🔑 Environment Variables

### Backend (`backend/.env`)
```env
PROJECT_NAME="AI Fitness Tracker"
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/fitness_db"
USE_POSTGRES=True
SECRET_KEY="your_super_secret_key_here"
ALGORITHM="HS256"
REDIS_HOST="localhost"
REDIS_PORT=6379
```

### Frontend (`frontend/.env`)
```env
REACT_APP_API_URL="http://localhost:8001"
```

---

## 🤖 How MediaPipe Works

The application uses the **MediaPipe Pose** library to process video frames from the user's webcam.

1. **Video Capture**: The `CameraView` component captures the webcam stream.
2. **Landmark Detection**: MediaPipe identifies 33 3D body landmarks (joints) at 30+ FPS.
3. **Skeleton Overlay**: Landmarks are drawn onto a canvas overlaying the video feed.
4. **State Machine Analysis**:
   - The `ExerciseStateMachine` calculates angles between joints (e.g., hip-knee-ankle for squats).
   - It tracks transitions between "START", "DOWN", and "UP" phases to count a valid repetition.
   - If a pose breaks (e.g., during a plank), the timer pauses or resets automatically.

---

## 🔌 API Connectivity

The frontend communicates with the backend via a centralized `useApi` hook:
- **Base URL**: Configured in `src/utils/api.js`.
- **Authentication**: JWT tokens are stored in `localStorage` and automatically attached to the `Authorization: Bearer <token>` header for all protected requests.
- **WebSocket**: Used for real-time chat and social notifications, connecting to `ws://localhost:8001/api/v1/ws`.

---

## 🛠️ Common Errors + Fixes

- **Camera Permission Denied**: Ensure your browser has permission to access the webcam. Check the lock icon in the address bar.
- **MediaPipe Not Loading**: Ensure you have a stable internet connection as the MediaPipe WASM binaries are often loaded from a CDN.
- **Backend CORS Error**: Verify that the frontend URL (e.g., `http://localhost:3000`) is added to the `allow_origins` list in `backend/app/main.py`.
- **PostgreSQL Connection Error**: Ensure the PostgreSQL service is running and the credentials in your `.env` match your local database setup.

---

## 📸 Screenshots

![Dashboard Placeholder](https://via.placeholder.com/800x450?text=App+Dashboard)
*Home Dashboard with weekly activity and stats.*

![Workout Placeholder](https://via.placeholder.com/800x450?text=Live+Workout+Detection)
*Real-time Squat detection with skeletal overlay.*

---

## 🌍 Deployment Notes

- **Frontend**: Can be hosted on Vercel, Netlify, or GitHub Pages. Ensure `REACT_APP_API_URL` points to your production backend.
- **Backend**: Can be deployed to Heroku, DigitalOcean, or AWS using the provided `Dockerfile`.
- **Database**: Use a managed service like AWS RDS, Supabase, or Railway for a cloud PostgreSQL instance. Update the `DATABASE_URL` in your production environment variables.

---

**Developed with ❤️ by [Harshitha Kakumanu](https://github.com/Kakumanu-Harshitha)**
