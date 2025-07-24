from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.db import get_db_connection  # ✅ Use session, not raw connection
from app.models.db import save_message  # ✅ Correct model
from app.services.chat_service import ChatManager

router = APIRouter()
chat_manager = ChatManager()

# ✅ WebSocket chat endpoint
@router.websocket("/ws/chat/{recipient_id}")
async def websocket_endpoint(websocket: WebSocket, recipient_id: str, db: Session = Depends(get_db_connection)):
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

# ✅ HTTP endpoint to fetch previous chat history
@router.get("/chat/history/{user1_id}/{user2_id}")
async def get_chat_history(user1_id: int, user2_id: int, db: Session = Depends(get_db_connection)):
    messages = db.query(save_message).filter(
        or_(
            and_(save_message.sender_id == user1_id, save_message.receiver_id == user2_id),
            and_(save_message.sender_id == user2_id, save_message.receiver_id == user1_id)
        )
    ).order_by(save_message.timestamp.asc()).all()

    return [
        {
            "from": m.sender_id,
            "to": m.receiver_id,
            "message": m.content,
            "timestamp": m.timestamp.isoformat()
        } for m in messages
    ]
