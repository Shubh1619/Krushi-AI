from typing import Dict
from fastapi import WebSocket
from app.models.db import save_message

class ChatManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections[username] = websocket
        print(f"✅ {username} connected. Active users: {list(self.active_connections.keys())}")

    def disconnect(self, username: str):
        self.active_connections.pop(username, None)
        print(f"❌ {username} disconnected. Active users: {list(self.active_connections.keys())}")

    async def get_user_id_by_username(self, db, username: str) -> int:
        with db.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE name = %s", (username,))
            result = cur.fetchone()
            if result:
                return result["id"]
            else:
                raise ValueError(f"🚫 User '{username}' not found in DB.")

    async def store_and_send(self, db, sender: str, recipient: str, content: str):
        try:
            sender_ws = self.active_connections.get(sender)
            recipient_ws = self.active_connections.get(recipient)

            sender_id = await self.get_user_id_by_username(db, sender)
            receiver_id = await self.get_user_id_by_username(db, recipient)

            save_message(sender_id, receiver_id, content)

            message_data = {
                "from": sender,
                "message": content
            }

            # Send to sender
            if sender_ws:
                await sender_ws.send_json(message_data)

            # Send to recipient
            if recipient_ws:
                await recipient_ws.send_json(message_data)
            else:
                print(f"📭 Recipient '{recipient}' is offline.")
        
        except Exception as e:
            print(f"🔥 Error in store_and_send: {str(e)}")
