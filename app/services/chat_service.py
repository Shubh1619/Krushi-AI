# # app/services/chat_manager.py

# from typing import List
# from fastapi import WebSocket

# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: List[WebSocket] = []
#         self.usernames = {}

#     async def connect(self, websocket: WebSocket, username: str):
#         await websocket.accept()
#         self.active_connections.append(websocket)
#         self.usernames[websocket] = username
#         await self.broadcast(f"🔵 {username} joined the chat.")

#     def disconnect(self, websocket: WebSocket):
#         username = self.usernames.get(websocket, "Unknown")
#         if websocket in self.active_connections:
#             self.active_connections.remove(websocket)
#         if websocket in self.usernames:
#             del self.usernames[websocket]

#     async def broadcast(self, message: str):
#         for connection in self.active_connections:
#             await connection.send_text(message)

# manager = ConnectionManager()
