# Deployment Guide (Free of Cost)

This guide provides step-by-step instructions to deploy the **AI Fitness Tracker** using free-tier services.

## 1. Database (PostgreSQL)
We recommend using **Neon** or **Supabase** for a free hosted PostgreSQL database.

### Neon Setup:
1. Go to [Neon.tech](https://neon.tech/) and create a free account.
2. Create a new project.
3. Copy the **Connection String** (it should look like `postgresql://user:password@host/dbname`).
4. Save this as your `DATABASE_URL`.

---

## 2. Backend (FastAPI)
We recommend **Render** for hosting the FastAPI backend.

### Render Setup:
1. Go to [Render.com](https://render.com/) and connect your GitHub repository.
2. Create a new **Web Service**.
3. Set the following:
   - **Name**: `ai-fitness-backend`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `backend/Dockerfile`
   - **Region**: Choose one closest to you.
4. Add **Environment Variables**:
   - `DATABASE_URL`: (Paste your Neon/Supabase URL here)
   - `USE_POSTGRES`: `True`
   - `GROQ_API_KEY`: (Your Groq API key)
   - `SECRET_KEY`: (Generate a random string)
5. Click **Create Web Service**. Render will give you a URL like `https://ai-fitness-backend.onrender.com`.

---

## 3. Web Client (Static Frontend)
Use **Vercel** to host the browser-based MediaPipe tracker.

### Vercel Setup:
1. Go to [Vercel.com](https://vercel.com/) and import your repository.
2. Set the **Root Directory** to `web`.
3. Click **Deploy**.

---

## Summary of Environment Variables
| Service | Variable Name | Source/Value |
| :--- | :--- | :--- |
| **Backend** | `DATABASE_URL` | Neon/Supabase Connection String |
| **Backend** | `USE_POSTGRES` | `True` |
| **Backend** | `GROQ_API_KEY` | Groq Dashboard |
---

### Note on Free Tiers:
- **Render**: The free tier "spins down" after 15 minutes of inactivity. The first request after a break might take 30-60 seconds to load.
- **Neon/Supabase**: Free tiers are generous but have storage limits (usually 500MB - 1GB), which is plenty for this app.
