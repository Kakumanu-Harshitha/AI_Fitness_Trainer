from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from ...websockets import manager
import json
from jose import jwt, JWTError
from ...core.config import settings
from typing import Optional
import base64
import numpy as np
import cv2
try:
    from ...core_ai.pose.pose_detector import detect_pose
except ImportError:
    print("Warning: Pose detector import failed.")
    def detect_pose(*args, **kwargs):
        return None, None, None
except Exception as e:
    print(f"Warning: Pose detector error: {e}")
    def detect_pose(*args, **kwargs):
        return None, None, None

from ...db.database import AsyncSessionLocal
from ...db.models import User, ChatMessage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

async def get_user_from_token(token: str, db: AsyncSession) -> Optional[User]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            return None
        
        result = await db.execute(select(User).filter(User.username == username))
        return result.scalars().first()
    except JWTError:
        return None

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = Query(None)):
    print(f"WS Connection Attempt. Token: {token[:15] if token else 'None'}...")
    await websocket.accept()
    
    # Check if it's a JWT or a username
    async with AsyncSessionLocal() as db:
        user = None
        if token:
            # Try JWT first
            user = await get_user_from_token(token, db)
            
            # If JWT fails, try as plain username (fallback for dev)
            if not user:
                print(f"WS Token decode failed, trying username fallback for: {token[:15]}...")
                result = await db.execute(select(User).filter(User.username == token))
                user = result.scalars().first()
        
        if not user:
            print("WS Reject: User not found or no token")
            await websocket.close(code=1008)
            return

        # If we reach here, user is authenticated
        user_id_str = user.username
        print(f"WS Authenticated: {user_id_str}")
        await manager.connect(websocket, user_id_str)
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message["type"] == "duel_request":
                    target_id = message["target_id"]
                    await manager.send_personal_message(json.dumps({
                        "type": "duel_invite",
                        "from": user_id_str,
                        "exercise": message["exercise"]
                    }), target_id)
                    
                elif message["type"] == "duel_accept":
                    challenger_id = message["challenger_id"]
                    exercise = message.get("exercise", "squats")
                    await manager.send_personal_message(json.dumps({
                        "type": "duel_start",
                        "opponent": user_id_str,
                        "exercise": exercise
                    }), challenger_id)
                    await manager.send_personal_message(json.dumps({
                        "type": "duel_start",
                        "opponent": challenger_id,
                        "exercise": exercise
                    }), user_id_str)
                    
                elif message["type"] == "duel_progress":
                    opponent_id = message["opponent_id"]
                    await manager.send_personal_message(json.dumps({
                        "type": "opponent_progress",
                        "reps": message["reps"]
                    }), opponent_id)

                elif message["type"] == "duel_end":
                    opponent_id = message["opponent_id"]
                    await manager.send_personal_message(json.dumps({
                        "type": "duel_finished",
                        "from": user_id_str,
                        "reps": message["reps"]
                    }), opponent_id)

                elif message["type"] == "chat_message":
                    # { "type": "chat_message", "target_username": "username", "message": "hello" }
                    target_username = message["target_username"]
                    chat_text = message["message"]
                    
                    # Find target user
                    res = await db.execute(select(User).filter(User.username == target_username))
                    target_user = res.scalars().first()
                    
                    if target_user:
                        # Save to DB
                        new_msg = ChatMessage(
                            sender_id=user.id,
                            receiver_id=target_user.id,
                            message=chat_text
                        )
                        db.add(new_msg)
                        await db.commit()
                        
                        # Send real-time
                        await manager.send_personal_message(json.dumps({
                            "type": "chat_received",
                            "from": user_id_str,
                            "message": chat_text,
                            "timestamp": new_msg.created_at.isoformat()
                        }), target_username)

        except WebSocketDisconnect:
            await manager.disconnect(websocket, user_id_str)

@router.websocket("/ws/vision")
async def vision_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "frame":
                # Decode base64 image
                img_data = base64.b64decode(message["image"])
                nparr = np.frombuffer(img_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    # Detect pose
                    _, landmarks = detect_pose(frame)
                    
                    if landmarks:
                        # Convert landmarks to serializable format
                        serializable_landmarks = []
                        for lm in landmarks:
                            serializable_landmarks.append({
                                "x": float(lm.x),
                                "y": float(lm.y),
                                "z": float(lm.z),
                                "visibility": float(lm.visibility)
                            })
                        
                        await websocket.send_text(json.dumps({
                            "type": "landmarks",
                            "landmarks": serializable_landmarks
                        }))
                    else:
                        await websocket.send_text(json.dumps({
                            "type": "no_pose"
                        }))
    except WebSocketDisconnect:
        print("Vision WS disconnected")
    except Exception as e:
        print(f"Vision WS error: {e}")
        await websocket.close()
