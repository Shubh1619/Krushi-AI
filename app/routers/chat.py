from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.chat_service import ChatManager
from app.models.db import get_db_connection

router = APIRouter()
chat_manager = ChatManager()


@router.websocket("/ws/chat/{recipient}")
async def chat_endpoint(websocket: WebSocket, recipient: str):
    username = websocket.query_params.get("username")
    if not username:
        await websocket.close()
        return
    await chat_manager.connect(username, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await chat_manager.send_message(sender=username, recipient=recipient, message=data)
    except WebSocketDisconnect:
        chat_manager.disconnect(username)
