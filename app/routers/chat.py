from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
from app.models.db import get_db_connection
from app.services.chat_service import ChatManager

router = APIRouter()
chat_manager = ChatManager()

@router.websocket("/ws/chat/{recipient_id}")
async def websocket_endpoint(websocket: WebSocket, recipient_id: str, db=Depends(get_db_connection)):
    user_id = websocket.query_params.get("user_id")

    if not user_id:
        await websocket.close(code=1008)
        return

    print(f"✅ User '{user_id}' connected to chat with recipient '{recipient_id}'")

    await chat_manager.connect(websocket, user_id)

    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message")

            print(f"📩 Message from {user_id} to {recipient_id}: {message}")

            if message:
                await chat_manager.store_and_send(db, user_id, recipient_id, message)

    except WebSocketDisconnect:
        print(f"❌ User '{user_id}' disconnected")
        chat_manager.disconnect(user_id)
