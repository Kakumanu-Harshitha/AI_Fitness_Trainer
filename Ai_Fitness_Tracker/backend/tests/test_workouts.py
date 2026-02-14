import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_workout_with_posture_score(async_client: AsyncClient):
    # 1. Register User
    register_payload = {
        "username": "testuser",
        "password": "testpassword"
    }
    response = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 200

    # 2. Login to get token
    login_payload = {
        "username": "testuser",
        "password": "testpassword"
    }
    response = await async_client.post("/api/v1/auth/login", json=login_payload)
    
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create Workout with Posture Score
    workout_payload = {
        "exercise": "squats",
        "reps": 10,
        "duration": 60,
        "avg_angle": 90.0,
        "calories": 50.0,
        "posture_score": 95.5 # Custom score
    }
    
    response = await async_client.post(
        "/api/v1/workouts/save", 
        json=workout_payload,
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["exercise"] == "squats"
    assert data["reps"] == 10
    assert data["posture_score"] == 95.5 # Verify our fix works
    assert "id" in data

@pytest.mark.asyncio
async def test_create_workout_default_posture_score(async_client: AsyncClient):
    # Reuse user or create new one? Since module scope fixture, DB persists.
    # Let's login again.
    login_payload = {
        "username": "testuser",
        "password": "testpassword"
    }
    response = await async_client.post("/api/v1/auth/login", json=login_payload)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    workout_payload = {
        "exercise": "pushups",
        "reps": 20,
        "duration": 40,
        "avg_angle": 0.0
        # No posture_score provided
    }
    
    response = await async_client.post(
        "/api/v1/workouts/save", 
        json=workout_payload,
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["posture_score"] == 85.0 # Verify default fallback works

@pytest.mark.asyncio
async def test_ghost_mode_replay_data(async_client: AsyncClient):
    login_payload = {
        "username": "testuser",
        "password": "testpassword"
    }
    response = await async_client.post("/api/v1/auth/login", json=login_payload)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a "Bad" workout (fewer reps)
    bad_workout = {
        "exercise": "ghost_test",
        "reps": 5,
        "duration": 30,
        "avg_angle": 0.0,
        "posture_score": 50.0,
        "replay_data": '[{"t":1, "score": 50}]'
    }
    await async_client.post("/api/v1/workouts/save", json=bad_workout, headers=headers)

    # 2. Create a "Best" workout (more reps)
    best_workout = {
        "exercise": "ghost_test",
        "reps": 15,
        "duration": 45,
        "avg_angle": 0.0,
        "posture_score": 90.0,
        "replay_data": '[{"t":1, "score": 90}]'
    }
    await async_client.post("/api/v1/workouts/save", json=best_workout, headers=headers)

    # 3. Fetch Best Workout
    response = await async_client.get("/api/v1/workouts/best/ghost_test", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["reps"] == 15
    assert data["replay_data"] == '[{"t":1, "score": 90}]'
