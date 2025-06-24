from fastapi import APIRouter, Body
from app.services.question_service import generate_ai_answer, save_question_to_db

router = APIRouter(prefix="/question", tags=["Expert Q&A"])

@router.post("/ask")
def ask_question(
    question: str = Body(...),
    crop: str = Body(...),
    language: str = Body(...),
    user_id: str = Body(...),
    state: str = Body(...),
    district: str = Body(...),
):
    """
    Ask a farming question. Returns AI (Gemini) answer.
    """
    ai_reply = generate_ai_answer(question, crop, language)
    saved = save_question_to_db(
        question, crop, language, user_id, state, district, ai_reply
    )
    return {"question_id": str(saved.inserted_id), "ai_answer": ai_reply}