from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
from app.models.db import get_db_connection
from app.services.chat_service import ChatManager

router = APIRouter()
chat_manager = ChatManager()

@router.websocket("/ws/chat/{recipient}")
async def websocket_endpoint(websocket: WebSocket, recipient: str, db=Depends(get_db_connection)):
    username = websocket.query_params.get("username")
    if not username:
        await websocket.close()
        return

    await chat_manager.connect(websocket, username)

    try:
        while True:
            data = await websocket.receive_json()
            sender = data.get("from")
            message = data.get("message")

            if sender and message:
                await chat_manager.store_and_send(db, sender, recipient, message)
    except WebSocketDisconnect:
        chat_manager.disconnect(username)
