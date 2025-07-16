# # app/routers/chat.py

# from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# from app.services.chat_service import manager
# from app.utils.token_utils import verify_token

# router = APIRouter()

# @router.websocket("/chat")
# async def websocket_chat(websocket: WebSocket):
#     token = websocket.query_params.get("token")

#     if not token:
#         await websocket.close(code=1008)
#         return

#     try:
#         user_data = verify_token(token)
#         username = user_data.get("name", "Anonymous")
#     except Exception:
#         await websocket.close(code=1008)
#         return

#     await manager.connect(websocket, username)

#     try:
#         while True:
#             data = await websocket.receive_text()
#             await manager.broadcast(f"{username}: {data}")
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
#         await manager.broadcast(f"🔴 {username} left the chat.")
