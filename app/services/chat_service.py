from typing import Dict
from fastapi import WebSocket
from app.models.db import save_message  # Updated to pass db session

class ChatManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)

    async def store_and_send(self, db, sender_id: str, recipient_id: str, content: str):
        # Save message to DB
        save_message(db, int(sender_id), int(recipient_id), content)

        message_data = {
            "from": sender_id,
            "to": recipient_id,
            "message": content
        }

        sender_ws = self.active_connections.get(sender_id)
        recipient_ws = self.active_connections.get(recipient_id)

        if sender_ws:
            await sender_ws.send_json(message_data)
        if recipient_ws:
            await recipient_ws.send_json(message_data)
