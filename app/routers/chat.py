from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
from app.models.db import get_db_connection
from app.services.chat_service import ChatManager

router = APIRouter()
chat_manager = ChatManager()

@router.websocket("/ws/chat/{recipient}")
async def websocket_endpoint(websocket: WebSocket, recipient: str, db=Depends(get_db_connection)):
    username = websocket.query_params.get("username")

    if not username:
        await websocket.close(code=1008)
        return

    print(f"✅ User '{username}' connected to chat with recipient '{recipient}'")

    await chat_manager.connect(websocket, username)

    try:
        while True:
            data = await websocket.receive_json()
            sender = data.get("from")
            message = data.get("message")

            print(f"📩 Message from {sender} to {recipient}: {message}")

            if sender and message:
                await chat_manager.store_and_send(db, sender, recipient, message)

    except WebSocketDisconnect:
        print(f"❌ User '{username}' disconnected")
        chat_manager.disconnect(username)
