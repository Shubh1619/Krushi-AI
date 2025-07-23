from typing import Dict
from fastapi import WebSocket
from app.models.db import save_message

class ChatManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, name: str, db):
        await websocket.accept()
        user_id = await self.get_user_id_by_name(db, name)
        self.active_connections[str(user_id)] = websocket  # Use ID as key

    def disconnect(self, user_id: str):
        self.active_connections.pop(str(user_id), None)


async def get_user_id_by_name(self, db, name: str) -> int:
    with db.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE name = %s", (name,))
        result = cur.fetchone()
        if result:
            return result["id"]
        else:
            raise ValueError(f"User '{name}' not found")

async def store_and_send(self, db, sender: str, recipient: str, content: str):
    sender_id = await self.get_user_id_by_name(db, sender)
    receiver_id = int(recipient)  # already passed as recipient ID
    save_message(sender_id, receiver_id, content)
    message_data = {
        "from": sender,
        "to": recipient,
        "message": content
    }
    sender_ws = self.active_connections.get(str(sender_id))
    recipient_ws = self.active_connections.get(str(receiver_id))
    if sender_ws:
        await sender_ws.send_json(message_data)
    if recipient_ws:
        await recipient_ws.send_json(message_data)