from fastapi import APIRouter, Query
from app.services.weather_service import get_full_weather, get_current_weather, get_crop_advisory

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/current")
def current_weather(city: str = Query(...)):
    return get_current_weather(city)

@router.get("/advisory")
def advisory(crop: str, stage: str, city: str):
    return get_crop_advisory(crop, stage, city)
