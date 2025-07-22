from typing import Dict
from fastapi import WebSocket
from sqlalchemy.orm import Session
from app.models.db import create_messages_table

class ChatManager:
    def __init__(self):
        # key = username, value = websocket connection
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections[username] = websocket

    def disconnect(self, username: str):
        self.active_connections.pop(username, None)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    # ✅ services/chat_service.py

async def store_and_send(self, db: Session, sender: str, recipient: str, content: str):
    # Save to DB (assuming you’ve wired sender/recipient IDs correctly)
    sender_ws = self.active_connections.get(sender)
    recipient_ws = self.active_connections.get(recipient)

    message_data = {
        "from": sender,
        "message": content
    }

    if sender_ws:
        await sender_ws.send_json(message_data)

    if recipient_ws:
        await recipient_ws.send_json(message_data)
