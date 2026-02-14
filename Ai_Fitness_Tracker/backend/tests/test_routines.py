import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_and_get_routines(async_client: AsyncClient):
    # 1. Register and Login
    register_payload = {"username": "routineuser", "password": "testpassword"}
    await async_client.post("/api/v1/auth/register", json=register_payload)
    
    login_payload = {"username": "routineuser", "password": "testpassword"}
    response = await async_client.post("/api/v1/auth/login", json=login_payload)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Routine
    routine_payload = {
        "name": "Morning Blast",
        "description": "Quick morning workout",
        "steps": [
            {
                "exercise_id": "pushups",
                "reps": 15,
                "sets": 3,
                "duration_seconds": 0
            },
            {
                "exercise_id": "squats",
                "reps": 20,
                "sets": 3,
                "duration_seconds": 0
            }
        ]
    }
    
    response = await async_client.post("/api/v1/routines/", json=routine_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Morning Blast"
    assert len(data["steps"]) == 2
    assert data["steps"][0]["exercise_id"] == "pushups"

    # 3. Get Routines
    response = await async_client.get("/api/v1/routines/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Morning Blast"
