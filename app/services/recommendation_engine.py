from app.config import GEMINI_API_KEY
import google.generativeai as genai
from fastapi import APIRouter
from app.services.recommendation_service import recommend_fertilizer

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")
router = APIRouter()

def recommend_fertilizer(crop: str, soil_type: str, n: int, p: int, k: int, area: float, stage: str) -> list:
    """
    Use Gemini to recommend fertilizers and quantities based on crop, soil, NPK, area, and stage.
    Returns a list of dicts with fertilizer, quantity_per_acre, and application_tip.
    """
    prompt = f"""
You are an agricultural assistant.
Given the crop, soil type, land area, and NPK values, suggest suitable fertilizers and their quantities.

Crop: {crop}
Soil Type: {soil_type}
NPK Values: N={n}, P={p}, K={k}
Land Area: {area} acres
Crop Stage: {stage}

Respond in JSON with:
- fertilizer name
- quantity per acre
- application tips
"""
    try:
        response = model.generate_content(prompt)
        import json
        return json.loads(response.text)
    except Exception as e:
        return [{"error": str(e)}]

@router.post("/recommend-fertilizer")
def recommend_fertilizer_api(
    crop: str,
    soil_type: str,
    n: int,
    p: int,
    k: int,
    area: float,
    stage: str
):
    """
    API endpoint to get fertilizer recommendations using Gemini.
    """
    return recommend_fertilizer(crop, soil_type, n, p, k, area, stage)