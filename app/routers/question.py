from fastapi import APIRouter, Query
from app.services.question_service import generate_ai_answer, save_question_to_db

router = APIRouter(prefix="/question")


@router.get("/ask")
def ask_question(
    question: str = Query(..., description="Your farming question in Marathi or Hindi"),
    state: str = Query(..., description="Your state (e.g., Maharashtra)")
):
    """
    Ask a farming question and get an AI-generated answer in Marathi.
    """
    ai_reply = generate_ai_answer(question, state)
    saved = save_question_to_db(question, state, ai_reply)
    return {
        "question_id": str(saved.inserted_id),
        "ai_answer": ai_reply
    }
