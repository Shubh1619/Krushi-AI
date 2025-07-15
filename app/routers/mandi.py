from fastapi import APIRouter, Query
from typing import Optional
from app.services.mandi_service import (
    get_latest_prices,
    get_price_history,
    get_best_market
)

router = APIRouter(prefix="/mandi", tags=["Mandi Rates"])

@router.get("/latest")
def latest_prices(crop: str, state: Optional[str] = None):
    return get_latest_prices(crop, state)

@router.get("/history")
def price_history(crop: str, district: str, days: int = 15):
    return get_price_history(crop, district, days)

@router.get("/best-market")
def best_market(crop: str, lat: float, lon: float):
    return get_best_market(crop, lat, lon)
