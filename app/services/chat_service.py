from typing import Dict
from fastapi import WebSocket
from app.models.db import save_message  # Uses psycopg2

class ChatManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"✅ Connection established for user: {user_id}")

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
        print(f"❌ Connection closed for user: {user_id}")

    async def store_and_send(self, sender_id: str, recipient_id: str, content: str):
        # Save message in DB
        save_message(int(sender_id), int(recipient_id), content)

        message_data = {
            "from": sender_id,
            "to": recipient_id,
            "message": content
        }

        # Send message to sender
        sender_ws = self.active_connections.get(sender_id)
        if sender_ws:
            await sender_ws.send_json(message_data)

        # Send message to recipient
        recipient_ws = self.active_connections.get(recipient_id)
        if recipient_ws:
            await recipient_ws.send_json(message_data)

        # Optional: Log for debugging
        print(f"📨 Sent message from {sender_id} to {recipient_id}: {content}")
