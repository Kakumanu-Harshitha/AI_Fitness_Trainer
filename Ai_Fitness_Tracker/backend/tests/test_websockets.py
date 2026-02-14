import pytest
from fastapi.testclient import TestClient
from app.main import app
import json

def test_duel_websocket_flow(client):
    # 1. Register and Login to get tokens for two users
    client.post("/api/v1/auth/register", json={"username": "user1", "password": "password123"})
    client.post("/api/v1/auth/register", json={"username": "user2", "password": "password123"})
    
    token1 = client.post("/api/v1/auth/login", json={"username": "user1", "password": "password123"}).json()["access_token"]
    token2 = client.post("/api/v1/auth/login", json={"username": "user2", "password": "password123"}).json()["access_token"]

    # 2. Connect both users to WebSocket
    with client.websocket_connect(f"/ws?token={token1}") as ws1:
        with client.websocket_connect(f"/ws?token={token2}") as ws2:
            
            # 3. User 1 invites User 2
            ws1.send_text(json.dumps({
                "type": "duel_request",
                "target_id": "user2",
                "exercise": "squats"
            }))
            
            # 4. User 2 receives invite
            # Skip any user_status messages (broadcasted on connection)
            while True:
                invite = json.loads(ws2.receive_text())
                if invite.get("type") != "user_status":
                    break
            
            assert invite["type"] == "duel_invite"
            assert invite["from"] == "user1"
            assert invite["exercise"] == "squats"
            
            # 5. User 2 accepts invite
            ws2.send_text(json.dumps({
                "type": "duel_accept",
                "challenger_id": "user1",
                "exercise": "squats"
            }))
            
            # 6. Both receive duel_start
            while True:
                start1 = json.loads(ws1.receive_text())
                if start1.get("type") != "user_status":
                    break
            
            while True:
                start2 = json.loads(ws2.receive_text())
                if start2.get("type") != "user_status":
                    break
            
            assert start1["type"] == "duel_start"
            assert start1["opponent"] == "user2"
            
            assert start2["type"] == "duel_start"
            assert start2["opponent"] == "user1"
            
            # 7. User 1 sends progress
            ws1.send_text(json.dumps({
                "type": "duel_progress",
                "opponent_id": "user2",
                "reps": 5
            }))
            
            # 8. User 2 receives progress
            progress = json.loads(ws2.receive_text())
            assert progress["type"] == "opponent_progress"
            assert progress["reps"] == 5
            
            # 9. User 1 ends duel
            ws1.send_text(json.dumps({
                "type": "duel_end",
                "opponent_id": "user2",
                "reps": 10
            }))
            
            # 10. User 2 receives duel_finished
            finished = json.loads(ws2.receive_text())
            assert finished["type"] == "duel_finished"
            assert finished["from"] == "user1"
            assert finished["reps"] == 10

def test_chat_websocket_flow(client):
    # 1. Register and Login
    client.post("/api/v1/auth/register", json={"username": "chat1", "password": "password123"})
    client.post("/api/v1/auth/register", json={"username": "chat2", "password": "password123"})
    
    token1 = client.post("/api/v1/auth/login", json={"username": "chat1", "password": "password123"}).json()["access_token"]
    token2 = client.post("/api/v1/auth/login", json={"username": "chat2", "password": "password123"}).json()["access_token"]

    # 2. Connect to WebSocket
    with client.websocket_connect(f"/ws?token={token1}") as ws1:
        with client.websocket_connect(f"/ws?token={token2}") as ws2:
            
            # 3. chat1 sends message to chat2
            ws1.send_text(json.dumps({
                "type": "chat_message",
                "target_username": "chat2",
                "message": "Hello from chat1"
            }))
            
            # 4. chat2 receives message
            msg = json.loads(ws2.receive_text())
            assert msg["type"] == "chat_received"
            assert msg["from"] == "chat1"
            assert msg["message"] == "Hello from chat1"
            assert "timestamp" in msg

            # 5. Check history via API
            history_res = client.get("/api/v1/social/chat/history/chat2", headers={"Authorization": f"Bearer {token1}"})
            assert history_res.status_code == 200
            history = history_res.json()
            assert len(history) >= 1
            assert history[-1]["message"] == "Hello from chat1"
