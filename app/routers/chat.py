from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.services.chat_service import ChatManager
from app.models.db import get_db_connection

router = APIRouter()
chat_manager = ChatManager()

# 🌐 WebSocket endpoint for real-time private chat
@router.websocket("/ws/chat/{recipient}")
async def websocket_endpoint(websocket: WebSocket, recipient: str):
    username = websocket.query_params.get("username")
    await chat_manager.connect(websocket, username)

    db: Session = next(get_db_connection())

    try:
        while True:
            data = await websocket.receive_json()
            sender = data.get("from")
            message = data.get("message")

            # Save and forward message
            await chat_manager.store_and_send(db, sender, recipient, message)

    except WebSocketDisconnect:
        chat_manager.disconnect(username)
