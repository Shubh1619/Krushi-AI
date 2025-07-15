from app.config import GEMINI_API_KEY
import google.generativeai as genai
from fastapi import APIRouter, HTTPException
from app.services.recommendation_service import recommend_fertilizer_marathi  # Updated import

genai.configure(api_key=GEMINI_API_KEY)

router = APIRouter()

@router.post("/recommend-fertilizer")
def recommend_fertilizer_api(
    crop: str,
    soil_type: str,
    stage: str
):
    """
    API endpoint to get fertilizer recommendations in Marathi using Gemini.
    """
    result = recommend_fertilizer_marathi(crop, soil_type, stage)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result