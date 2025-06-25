from fastapi import APIRouter, Body
from app.services.finance_service import (
    add_finance_record,
    get_all_finance_records,
    get_records_by_crop
)

router = APIRouter(prefix="/finance", tags=["Investment & Income"])

@router.post("/add")
def add_record(
    crop: str = Body(...),
    season: str = Body(...),
    expenses: dict = Body(...),
    income: dict = Body(...)
):
    """
    Add a finance entry. Income must have: quantity, rate_per_kg
    """
    return add_finance_record(crop, season, expenses, income)

@router.get("/all")
def get_all():
    return get_all_finance_records()

@router.get("/crop/{crop_name}")
def get_by_crop(crop_name: str):
    return get_records_by_crop(crop_name)
