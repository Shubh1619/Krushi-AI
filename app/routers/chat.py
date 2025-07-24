from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.models.db import get_chat_history  # Uses psycopg2
from app.services.chat_service import ChatManager

router = APIRouter()
chat_manager = ChatManager()

# ✅ WebSocket endpoint for real-time chat
@router.websocket("/ws/chat/{recipient_id}")
async def websocket_endpoint(websocket: WebSocket, recipient_id: str):
    user_id = websocket.query_params.get("user_id")

    if not user_id:
        await websocket.close(code=1008)
        return

    print(f"🟢 WebSocket connected: user_id={user_id}, recipient_id={recipient_id}")
    await chat_manager.connect(websocket, user_id)

    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message")
            print(f"📩 Received message from {user_id} to {recipient_id}: {message}")

            if message:
                await chat_manager.store_and_send(user_id, recipient_id, message)

    except WebSocketDisconnect:
        chat_manager.disconnect(user_id)
        print(f"🔴 WebSocket disconnected: user_id={user_id}")

# ✅ HTTP endpoint to fetch chat history
@router.get("/chat/history/{user1_id}/{user2_id}")
async def get_chat_history_route(user1_id: int, user2_id: int):
    messages = get_chat_history(user1_id, user2_id)
    return messages
