from app.config import GEMINI_API_KEY
import google.generativeai as genai
from fastapi import APIRouter, HTTPException
from app.services.recommendation_service import recommend_fertilizer

genai.configure(api_key=GEMINI_API_KEY)

router = APIRouter()

@router.post("/recommend-fertilizer")
def recommend_fertilizer_api(
    crop: str,
    soil_type: str,
    stage: str
):
    """
    API endpoint to get fertilizer recommendations using Gemini.
    """
    result = recommend_fertilizer(crop, soil_type, stage)
    if result and isinstance(result, list) and "error" in result[0]:
        raise HTTPException(status_code=400, detail=result[0]["error"])
    return result