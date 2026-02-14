from typing import List, Dict
from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        # Map user_id (str) -> List of WebSockets (for multi-tab support)
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        # We don't need to accept here anymore as it's handled in the endpoint
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
            # Broadcast user online status ONLY on first connection
            await self.broadcast(json.dumps({
                "type": "user_status",
                "user_id": user_id,
                "status": "online"
            }))
        
        if websocket not in self.active_connections[user_id]:
            self.active_connections[user_id].append(websocket)
        
        print(f"User {user_id} connected. Active tabs: {len(self.active_connections[user_id])}")

    async def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                # Broadcast user offline status ONLY when last connection is closed
                await self.broadcast(json.dumps({
                    "type": "user_status",
                    "user_id": user_id,
                    "status": "offline"
                }))
        
        print(f"User {user_id} disconnected. Remaining tabs: {len(self.active_connections.get(user_id, []))}")

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            # Send to all active tabs for this user
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except:
                    # Connection might be stale
                    pass

    async def broadcast(self, message: str):
        for connections in self.active_connections.values():
            for connection in connections:
                try:
                    await connection.send_text(message)
                except:
                    pass

manager = ConnectionManager()
