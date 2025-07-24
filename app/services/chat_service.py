from typing import Dict
from fastapi import WebSocket
from app.models.db import save_message

class ChatManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)

    async def store_and_send(self, sender_id: str, receiver_id: str, message: str):
        # Save to DB
        save_message(int(sender_id), int(receiver_id), message)

        # Deliver to receiver if online
        if receiver_id in self.active_connections:
            await self.active_connections[receiver_id].send_json({
                "from": sender_id,
                "to": receiver_id,
                "message": message
            })

        # Echo back to sender
        if sender_id in self.active_connections:
            await self.active_connections[sender_id].send_json({
                "from": sender_id,
                "to": receiver_id,
                "message": message
            })
