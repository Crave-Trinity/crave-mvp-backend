#====================================================
# File: app/api/endpoints/live_updates.py
# Usage: now sub can be cast to int directly
#====================================================

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, Query, Depends
from sqlalchemy.orm import Session
from typing import Dict, List, Any
from datetime import datetime

from app.infrastructure.auth.jwt_handler import decode_access_token
from app.infrastructure.database.session import get_db

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections.setdefault(user_id, []).append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections and websocket in self.active_connections[user_id]:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: Any, user_id: int):
        if user_id in self.active_connections:
            for ws in self.active_connections[user_id]:
                try:
                    await ws.send_json(message)
                except:
                    self.disconnect(ws, user_id)

    async def broadcast(self, message: Any):
        disconnected_users = []
        for uid, connections in self.active_connections.items():
            disconnected = []
            for ws in connections:
                try:
                    await ws.send_json(message)
                except:
                    disconnected.append(ws)
            for ws in disconnected:
                self.active_connections[uid].remove(ws)
            if not self.active_connections[uid]:
                disconnected_users.append(uid)
        for uid in disconnected_users:
            del self.active_connections[uid]

manager = ConnectionManager()

@router.websocket("/live-updates")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(None),
    db: Session = Depends(get_db)
):
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))  # now safe to cast
        await manager.connect(websocket, user_id)
        
        await websocket.send_json({
            "type": "connection_established",
            "message": "Connected to real-time updates",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id
        })

        while True:
            data = await websocket.receive_json()
            await manager.send_personal_message(
                {
                    "type": "echo",
                    "message": "Server received your message",
                    "data": data,
                    "timestamp": datetime.utcnow().isoformat()
                },
                user_id
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

# Done. Now sub is always an integer ID, matching user_id = int(payload.get("sub")).