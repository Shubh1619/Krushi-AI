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

    async def store_and_send(self, db: Session, sender: str, recipient: str, content: str):
        # 1️⃣ Save message to DB
        db_message = create_messages_table(sender=sender, recipient=recipient, content=content)
        db.add(db_message)
        db.commit()

        # 2️⃣ Send to sender
        sender_ws = self.active_connections.get(sender)
        if sender_ws:
            await sender_ws.send_json(f"👤 You: {content}")

        # 3️⃣ Send to recipient
        recipient_ws = self.active_connections.get(recipient)
        if recipient_ws:
            await recipient_ws.send_text(f"💬 {sender}: {content}")
