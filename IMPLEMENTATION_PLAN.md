# 🛠️ TECHNICAL IMPLEMENTATION ROADMAP: FitVision AI

This document serves as the **Master Build Plan**. It outlines the exact engineering steps required to move from documentation to a fully functional, production-ready AI Fitness Tracker.

---

## 🏗️ PHASE 1: CORE ARCHITECTURE SETUP
*Goal: Establish the communication bridge between the AI edge and the persistent backend.*

### 1.1 Backend Foundation (FastAPI)
- **Database Schema**: Finalize PostgreSQL models for `Users`, `WorkoutLogs`, `WaterLogs`, `Streaks`, and `ChatMessages`.
- **Async Engine**: Configure `SQLAlchemy` with `asyncpg` for high-concurrency handling.
- **Auth Layer**: Implement JWT-based security with password hashing (`Passlib`).
- **WebSocket Gateway**: Set up a centralized WebSocket manager to handle real-time social updates and chat.

### 1.2 Frontend Foundation (React)
- **State Architecture**: Implement `WorkoutContext` to manage live session data (reps, score, timer).
- **API Wrapper**: Build a custom `useApi` hook with interceptors for token management.
- **Routing**: Secure private routes (Dashboard, Live Workout) from public ones (Login, Signup).

---

## 🤖 PHASE 2: AI KINEMATIC ENGINE (The "Brain")
*Goal: Turn raw video coordinates into intelligent fitness data.*

### 2.1 MediaPipe Integration
- **Pipeline**: Set up the `Pose` detector to run on the browser's requestAnimationFrame loop.
- **Canvas Overlay**: Implement a high-performance drawing utility to render the 33-point skeleton without UI lag.

### 2.2 Exercise State Machines
- **Logic Blocks**: Create modular engines for each exercise:
    - `SquatEngine`: Tracks hip/knee/ankle angles.
    - `PushupEngine`: Tracks shoulder/elbow/wrist alignment and depth.
    - `PlankEngine`: Monitors landmark variance to detect "sagging" or "breaking."
- **Feedback Loop**: Implement real-time string generators (e.g., "Go Lower!", "Keep Back Straight!") based on angle thresholds.

---

## 📊 PHASE 3: WELLNESS & GAMIFICATION LOGIC
*Goal: Transform data into motivation.*

### 3.1 The PHI (Performance Health Index)
- **Algorithm**: Develop the logic to calculate:
    - `Joint Stress`: (100 - Average Form Score).
    - `Recovery Rate`: (Initial Health - (Workouts_Today * Fatigue_Constant)).
- **Hydration Sync**: Connect the `WaterTracker` component to the backend to persist daily intake.

### 3.2 Social Connectivity
- **Real-time Leaderboard**: Implement a background worker to broadcast rank changes via WebSockets whenever a workout is logged.
- **Chat System**: Build the UI/UX for the messaging drawer, ensuring low-latency delivery using the WS gateway.

---

## 🧪 PHASE 4: VERIFICATION & EDGE-CASE HANDLING
*Goal: Ensure the system is "Hackathon-Proof."*

### 4.1 Calibration & Threshold Tuning
- **Lighting Robustness**: Adjust MediaPipe confidence thresholds (0.3 - 0.5) to handle varying room environments.
- **False Positive Filter**: Implement a "Debounce" logic for rep counting to prevent double-counting accidental movements.

### 4.2 Error Boundaries
- **Camera Recovery**: Add logic to handle "Camera Lost" or "Permission Denied" gracefully.
- **Offline Sync**: Implement local storage fallbacks so users don't lose workout data if the connection drops.

---

## 🚀 PHASE 5: DEPLOYMENT & SCALING
*Goal: Making the app accessible to the world.*

- **Containerization**: Finalize `Dockerfile` for the backend.
- **Cloud DB**: Migrate local SQLite/PostgreSQL to a managed cloud instance (e.g., Supabase or AWS RDS).
- **Frontend Hosting**: Deploy the React build to Vercel/Netlify with environment variable mapping.

---

## 📅 HACKATHON BUILD TIMELINE (Example)
- **Day 1 (AM)**: Backend API + DB Schema + Auth.
- **Day 1 (PM)**: Frontend UI Skeleton + Context Setup.
- **Day 2 (AM)**: **CRITICAL**: MediaPipe Integration + Squat/Pushup State Machines.
- **Day 2 (PM)**: WebSockets + Chat + Leaderboard.
- **Day 3 (AM)**: Bug fixing + Polish + PHI Logic.
- **Day 3 (PM)**: Documentation + Presentation Prep.

---
**Status**: Ready for Implementation.
**Lead Engineer**: Harshitha Kakumanu
