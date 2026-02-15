# 📝 SOFTWARE REQUIREMENTS SPECIFICATION (SRS): FitVision AI

**Version:** 1.0  
**Project:** FitVision AI (AI Fitness Tracker)  
**Status:** Approved for Implementation

---

## 1. 📘 INTRODUCTION

### 1.1 Purpose
The purpose of this document is to define the functional and non-functional requirements for **FitVision AI**, a computer-vision-based fitness application. This system aims to solve the "home workout supervision gap" by providing real-time biomechanical analysis, form validation, and automated rep counting using standard webcams.

### 1.2 Scope
FitVision AI is a web-based application (with potential for mobile wrapping) that:
1.  Uses **MediaPipe Pose** (Edge-AI) to detect 33 skeletal landmarks in real-time.
2.  Validates exercise form against professional biomechanical standards.
3.  Counts repetitions **only** when form is correct.
4.  Provides gamified social features (Leaderboards, Chat, Streaks) to improve retention.
5.  Tracks long-term health metrics via a Performance Health Index (PHI).

### 1.3 Definitions & Acronyms
*   **Edge-AI**: Artificial Intelligence algorithms running locally on the user's device.
*   **Landmarks**: Key points on the human body (e.g., Left Elbow, Right Knee) identified by the vision model.
*   **PHI**: Performance Health Index - A proprietary metric combining consistency, form quality, and recovery.
*   **JWT**: JSON Web Token, used for stateless authentication.
*   **SPA**: Single Page Application (React).

---

## 2. 👥 OVERALL DESCRIPTION

### 2.1 User Characteristics
*   **The Beginner**: Unfamiliar with exercise mechanics. High risk of injury. Needs "guardrails" and constant feedback.
*   **The Remote Athlete**: Experienced but lacks a spotter. Needs objective data on range of motion and tempo.
*   **The Competitor**: Motivated by social ranking and beating personal bests.

### 2.2 Product Perspective
This system operates as a **Hybrid Client-Server Application**:
*   **Client (Frontend)**: Handles heavy lifting (AI Inference, Video Rendering) to ensure privacy and low latency.
*   **Server (Backend)**: Handles persistence (User Data, History), social relay (Chat, Leaderboards), and authentication.

---

## 3. 🛠️ FUNCTIONAL REQUIREMENTS

### 3.1 🔐 Authentication & Security
*   **FR-AUTH-01**: Users must register with Email, Username, and Password.
*   **FR-AUTH-02**: Passwords must be hashed using **Bcrypt** before storage.
*   **FR-AUTH-03**: System must issue **JWT Access Tokens** upon successful login.
*   **FR-AUTH-04**: Protected routes (Dashboard, Workout) must validate the JWT before rendering.

### 3.2 🏋️ AI Kinematic Engine (The Core)
*   **FR-AI-01**: System must initialize the camera feed and run MediaPipe Pose inference at a minimum of **15 FPS**.
*   **FR-AI-02**: System must draw a skeletal overlay on the video feed in real-time (<50ms latency).
*   **FR-AI-03 (State Machine)**:
    *   **Squat**: Track Hip-Knee-Ankle angle. Valid Rep = Hip descends below Knee level (<100°).
    *   **Pushup**: Track Shoulder-Elbow-Wrist angle. Valid Rep = Elbow flexion > 90°.
    *   **Plank**: Track Shoulder-Hip-Ankle linearity. Invalid if hip variance > 15°.
*   **FR-AI-04 (Smart Counting)**: The system must **NOT** increment the rep counter if:
    *   The user does not reach full range of motion.
    *   The confidence score of landmarks drops below 0.5.
*   **FR-AI-05 (Feedback)**: System must generate text-to-speech or on-screen text alerts for errors (e.g., "Keep your back straight").

### 3.3 📊 Analytics & Progress
*   **FR-DATA-01**: System must save `WorkoutLog` entries containing: Exercise Type, Rep Count, Duration, Avg Form Score, and Timestamp.
*   **FR-DATA-02**: System must calculate **Joint Stress** based on the inverse of the average form score.
*   **FR-DATA-03**: System must track daily water intake via a `WaterLog` feature.
*   **FR-DATA-04**: System must visualize progress charts (Weekly Reps, PHI Trend) on the Dashboard.

### 3.4 🎮 Social & Gamification
*   **FR-SOC-01**: **Live Leaderboard**: System must update user rankings in real-time using WebSockets when a workout is completed.
*   **FR-SOC-02**: **Global Chat**: Users must be able to send messages to a public room.
*   **FR-SOC-03**: **Streak System**: System must track consecutive days of activity. If a user misses 24h, the streak resets to 0.

---

## 4. ⚙️ NON-FUNCTIONAL REQUIREMENTS (NFR)

### 4.1 Performance
*   **NFR-PERF-01**: AI Inference must not consume more than 60% of CPU on an average laptop (i5 or equivalent) to prevent freezing.
*   **NFR-PERF-02**: API Response time for database queries must be under **200ms**.
*   **NFR-PERF-03**: WebSocket message delivery latency should be under **100ms**.

### 4.2 Privacy
*   **NFR-PRIV-01**: **Zero-Upload Policy**: No raw video data or images shall ever be sent to the backend server. All processing is local.
*   **NFR-PRIV-02**: User passwords and personal data must be encrypted at rest and in transit.

### 4.3 Reliability
*   **NFR-REL-01**: If the camera is disconnected, the system must pause the workout and prompt the user.
*   **NFR-REL-02**: The application must gracefully handle network disconnections by caching the current workout session locally.

---

## 5. 🔌 EXTERNAL INTERFACE REQUIREMENTS

### 5.1 User Interfaces
*   **Dashboard**: Clean, dark-mode card layout displaying stats.
*   **Live Workout**: Full-screen video with overlay HUD (Heads-Up Display) for Reps, Timer, and Feedback.
*   **Mobile Responsiveness**: UI must adapt to mobile viewports (stacking columns).

### 5.2 Hardware Interfaces
*   **Input**: Standard USB Webcam or Built-in Laptop Camera (720p resolution recommended).
*   **Output**: Screen (Visual Overlay) and Audio (TTS Feedback).

### 5.3 Software Interfaces
*   **Database**: PostgreSQL (v13+) via `asyncpg`.
*   **AI Library**: `@mediapipe/pose` (JavaScript/WASM).
*   **Backend Framework**: FastAPI (Python 3.9+).

---

## 6. 📅 IMPLEMENTATION CONSTRAINTS
*   **IC-01**: Must run in a modern browser (Chrome, Firefox, Edge) with WebGL support.
*   **IC-02**: Must not require a dedicated GPU (must run on CPU/Integrated Graphics).
