# 🏗️ SYSTEM DESIGN: FitVision AI

## 1. 🌐 HIGH-LEVEL ARCHITECTURE
**FitVision AI** employs a **Hybrid Client-Server Architecture** to balance real-time responsiveness with persistent data management.

### 1.1 Architecture Diagram (Conceptual)
```mermaid
graph TD
    User[Webcam/Browser] -->|Local Inference| AI[MediaPipe Pose (Client-Side)]
    AI -->|Valid Reps/Angles| Frontend[React SPA]
    Frontend -->|REST API (Auth, History)| API[FastAPI Gateway]
    Frontend -->|WebSocket (Chat, Leaderboard)| WS[WebSocket Manager]
    API -->|Async ORM| DB[(PostgreSQL)]
    WS -->|Pub/Sub| DB
```

### 1.2 Key Architectural Decisions
*   **Client-Side AI (Edge Processing)**: We execute the Pose Detection model directly in the user's browser (React + MediaPipe JS). This guarantees **Zero Latency** for feedback and maintains **100% User Privacy** (no video leaves the device).
*   **Event-Driven WebSocket Layer**: Real-time features (Chat, Leaderboard) utilize persistent WebSocket connections for instant updates, avoiding polling overhead.
*   **Stateless REST API**: The backend is stateless, relying on JWT for authentication, allowing horizontal scaling.

## 2. 🖥️ FRONTEND DESIGN (React)
### 2.1 Component Structure
*   **Core Contexts**:
    *   `AuthContext`: Manages JWT tokens and user session.
    *   `WorkoutContext`: Central store for active workout state (reps, timer, current exercise, form validity).
    *   `SocketContext`: Manages WebSocket connection and event subscriptions.
*   **Key Screens**:
    *   `Dashboard`: User stats overview, start workout button.
    *   `LiveWorkout`: The "AI Coach" view. Renders webcam feed + skeleton overlay + stats HUD.
    *   `Leaderboard`: Real-time ranking list.
    *   `Profile`: User settings and history.

### 2.2 State Management Pattern (Workout)
1.  **Input**: Webcam frame captured.
2.  **Process**: MediaPipe generates 33 landmarks (x, y, z, visibility).
3.  **Analyze**: `ExerciseEngine` calculates joint angles (e.g., Knee Angle).
4.  **Evaluate**: State Machine determines phase (START -> DOWN -> UP).
5.  **Update**: If rep valid -> Increment Rep Count -> Update Context -> Send to Backend (optional batching).

## 3. 🤖 AI & KINEMATIC ENGINE DESIGN
### 3.1 Pose Detection Pipeline
*   **Model**: MediaPipe Pose (Google).
*   **Configuration**:
    *   `modelComplexity`: 1 (Balanced for speed/accuracy).
    *   `smoothLandmarks`: true (Reduces jitter).
    *   `minDetectionConfidence`: 0.5.
    *   `minTrackingConfidence`: 0.5.

### 3.2 Exercise State Machines (Logic)
Each exercise is an independent Class/Module implementing a standard interface:
*   `SquatEngine`:
    *   **Joints**: Hip, Knee, Ankle.
    *   **Logic**: Track knee flexion angle.
        *   `START`: Angle > 160°.
        *   `DOWN`: Angle < 100° (Valid Rep Threshold).
        *   `UP`: Angle > 160° (Complete Rep).
*   **Feedback System**:
    *   Calculates deviation from ideal form.
    *   Generates string feedback: "Go Lower", "Knees Out", "Good Job".

## 4. 🔙 BACKEND DESIGN (FastAPI)
### 4.1 API Structure
*   `/api/v1/auth`: Login, Register (OAuth2PasswordRequestForm).
*   `/api/v1/workouts`: CRUD for `WorkoutLog`.
*   `/api/v1/stats`: Aggregated user statistics.
*   `/api/v1/social`: Chat history and leaderboard data.
*   `/ws`: WebSocket endpoint for real-time events.

### 4.2 Database Schema (PostgreSQL)
*   **Users**: `id (PK), email, password_hash, username, created_at`.
*   **WorkoutLogs**: `id (PK), user_id (FK), exercise_type, reps, duration, avg_score, created_at`.
*   **ChatMessages**: `id (PK), user_id (FK), content, timestamp`.
*   **Streaks**: `user_id (PK/FK), current_streak, last_activity_date`.
*   **WaterLogs**: `id (PK), user_id (FK), amount_ml, date`.

## 5. 🔒 SECURITY DESIGN
*   **Authentication**: JWT (JSON Web Tokens) with expiration.
*   **Password Storage**: Bcrypt hashing.
*   **CORS Policy**: Restrict API access to trusted frontend domains.
*   **Input Validation**: Pydantic models for strict request body validation.

## 6. 🚀 DEPLOYMENT STRATEGY
*   **Containerization**: Dockerfile for backend (Python:3.9-slim).
*   **Database**: Managed PostgreSQL (e.g., Supabase/RDS).
*   **Frontend**: Static hosting (Vercel/Netlify).
*   **CI/CD**: GitHub Actions for automated testing and deployment.
