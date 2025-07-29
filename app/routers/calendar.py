from fastapi import APIRouter, Body
from app.services.calendar_json_service import (
    add_new_crop, get_crop_lifecycle, save_calendar, delete_task_by_date
)

router = APIRouter(prefix="/calendar", tags=["Crop Calendar"])

@router.post("/add-crop")
def add_crop(
    crop_name: str = Body(...),
    lifecycle: list = Body(...)
):
    """
    Add a new crop and its lifecycle.
    Each lifecycle item must have 'day', 'task', 'tip'
    """
    return add_new_crop(crop_name, lifecycle)

@router.post("/generate")
def generate_calendar(
    crop_name: str = Body(...),
    sowing_date: str = Body(...)
):
    lifecycle = get_crop_lifecycle(crop_name)
    if not lifecycle:
        from app.services.calendar_json_service import read_crops
        return {
            "error": f"No lifecycle found for '{crop_name}'",
            "available": list(read_crops().keys())
        }
    saved = save_calendar(crop_name, sowing_date, lifecycle)
    return {"message": "Calendar created", "tasks": saved}

@router.delete("/complete")
def complete_task(
    date: str = Body(...),
    task: str = Body(...)
):
    return delete_task_by_date(date, task)
