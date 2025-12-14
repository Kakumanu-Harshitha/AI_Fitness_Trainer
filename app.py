import streamlit as st
import requests
import subprocess
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

# ================= CONFIG =================
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Fitness Trainer",
    layout="wide"
)

# ================= SESSION STATE =================
for key in ["token", "user", "age", "weight", "height"]:
    if key not in st.session_state:
        st.session_state[key] = None


# ================= AUTH PAGE =================
if not st.session_state.token:
    st.title("🏋️ AI Fitness Trainer")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    # ---------- LOGIN ----------
    if col1.button("Login"):
        res = requests.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password}
        )

        if res.status_code == 200:
            data = res.json()
            st.session_state.token = data["token"]
            st.session_state.user = data["user"]

            headers = {
                "Authorization": f"Bearer {st.session_state.token}"
            }

            profile_res = requests.get(
                f"{API_URL}/profile",
                headers=headers
            )

            if profile_res.status_code == 200:
                profile = profile_res.json()
                st.session_state.age = profile.get("age")
                st.session_state.weight = profile.get("weight_kg")
                st.session_state.height = profile.get("height_cm")

            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

    # ---------- REGISTER ----------
    if col2.button("Register"):
        res = requests.post(
            f"{API_URL}/auth/register",
            json={"username": username, "password": password}
        )

        if res.status_code == 200:
            st.success("Registered successfully. Please login.")
        else:
            st.error("Registration failed")

    st.stop()


# ================= SIDEBAR PROFILE =================
st.sidebar.markdown("## 👤 User Profile")
st.sidebar.write(f"**Username:** {st.session_state.user['username']}")

st.session_state.age = st.sidebar.slider(
    "Age", 10, 80,
    value=st.session_state.age or 25
)

st.session_state.weight = st.sidebar.number_input(
    "Weight (kg)", 30.0, 150.0,
    value=st.session_state.weight or 60.0,
    step=0.5
)

st.session_state.height = st.sidebar.number_input(
    "Height (cm)", 120.0, 220.0,
    value=st.session_state.height or 165.0,
    step=0.5
)

# ---------- SAVE PROFILE ----------
if st.sidebar.button("💾 Save Profile"):
    headers = {
        "Authorization": f"Bearer {st.session_state.token}"
    }

    payload = {
        "age": st.session_state.age,
        "weight_kg": st.session_state.weight,
        "height_cm": st.session_state.height
    }

    response = requests.post(
        f"{API_URL}/profile",
        json=payload,
        headers=headers
    )

    if response.status_code == 200:
        st.sidebar.success("✅ Profile saved successfully")
    else:
        st.sidebar.error("❌ Failed to save profile")

# ---------- BMI ----------
if st.session_state.height and st.session_state.weight:
    bmi = round(
        st.session_state.weight / ((st.session_state.height / 100) ** 2),
        2
    )
else:
    bmi = 0

if bmi < 18.5:
    bmi_status = "Underweight"
elif bmi < 25:
    bmi_status = "Healthy"
elif bmi < 30:
    bmi_status = "Overweight"
else:
    bmi_status = "Obese"

st.sidebar.markdown("---")
st.sidebar.write(f"**BMI:** {bmi}")
st.sidebar.write(f"**Status:** {bmi_status}")

# ---------- LOGOUT ----------
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()


# ================= MAIN DASHBOARD =================
st.title("🤖 AI Fitness Trainer Dashboard")

health_score = max(50, int(100 - abs(22 - bmi) * 4))
st.metric("🧠 Health Score", f"{health_score} / 100")


# ================= EXERCISE =================
st.markdown("## 🏃 Select Exercise")

exercise = st.selectbox(
    "Exercise",
    ["squat", "pushup", "plank", "tree_pose", "chair_pose", "high_knees"]
)

exercise_tips = {
    "squat": "Keep your back straight and knees behind toes.",
    "pushup": "Engage your core and keep body straight.",
    "plank": "Maintain a straight line.",
    "tree_pose": "Focus on balance and breathing.",
    "chair_pose": "Sit like an invisible chair.",
    "high_knees": "Lift knees high and keep rhythm."
}

st.info(f"💡 Tip: {exercise_tips[exercise]}")

# ---------- START EXERCISE ----------
if st.button("▶ Start Exercise"):
    st.success("Camera started. Press Q to stop.")

    env = os.environ.copy()
    env["ACTIVE_EXERCISE"] = exercise
    env["USER_TOKEN"] = st.session_state.token

    SCRIPT_PATH = os.path.join(os.getcwd(), "src", "main.py")

    subprocess.Popen(
        [sys.executable, SCRIPT_PATH],
        env=env
    )


# ================= WORKOUT HISTORY =================
st.markdown("## 📊 Workout History")

headers = {
    "Authorization": f"Bearer {st.session_state.token}"
}

res = requests.get(
    f"{API_URL}/workouts/my",
    headers=headers
)

if res.status_code == 200 and res.json():
    df = pd.DataFrame(res.json())
    st.dataframe(df, use_container_width=True)

    st.markdown("### 🔥 Calories Burned (by Exercise)")
    grouped = df.groupby("exercise")["calories"].sum()

    fig, ax = plt.subplots()
    ax.bar(grouped.index, grouped.values)
    ax.set_ylabel("Calories")
    ax.set_xlabel("Exercise")
    st.pyplot(fig)
else:
    st.info("No workouts yet")


# ================= EXPORT =================
if res.status_code == 200 and res.json():
    csv = df.to_csv(index=False)
    st.download_button(
        "⬇ Download Workout Report",
        csv,
        "fitness_report.csv",
        "text/csv"
    )
