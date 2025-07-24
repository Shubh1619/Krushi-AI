from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.chat_service import ChatManager
from app.models.db import get_chat_history

router = APIRouter()
chat_manager = ChatManager()

@router.websocket("/ws/chat/{recipient_id}")
async def websocket_endpoint(websocket: WebSocket, recipient_id: str):
    user_id = websocket.query_params.get("user_id")
    if not user_id:
        await websocket.close(code=1008)
        return

    await chat_manager.connect(websocket, user_id)

    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message")
            if message:
                await chat_manager.store_and_send(user_id, recipient_id, message)
    except WebSocketDisconnect:
        chat_manager.disconnect(user_id)

@router.get("/chat/history/{user1}/{user2}")
def fetch_history(user1: int, user2: int):
    return get_chat_history(user1, user2)
