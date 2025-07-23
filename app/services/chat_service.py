from typing import Dict
from fastapi import WebSocket
from app.models.db import save_message

class ChatManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections[username] = websocket

    def disconnect(self, username: str):
        self.active_connections.pop(username, None)

    async def get_user_id_by_username(self, db, username: str) -> int:
        with db.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            result = cur.fetchone()
            if result:
                return result["id"]
            else:
                raise ValueError(f"User '{username}' not found")

    async def store_and_send(self, db, sender: str, recipient: str, content: str):
        sender_ws = self.active_connections.get(sender)
        recipient_ws = self.active_connections.get(recipient)

        sender_id = await self.get_user_id_by_username(db, sender)
        receiver_id = await self.get_user_id_by_username(db, recipient)

        save_message(sender_id, receiver_id, content)

        message_data = {
            "from": sender,
            "to": recipient,
            "message": content
        }

        if sender_ws:
            await sender_ws.send_json(message_data)
        if recipient_ws:
            await recipient_ws.send_json(message_data)
