from fastapi import APIRouter, Query
from app.services.scheme_service import (
    get_all_schemes,
    get_scheme_by_id,
    get_recommended_schemes,
    get_gemini_schemes,
    get_all_states,
    get_districts_by_state
)

router = APIRouter(
    prefix="/schemes",
    tags=["Government Schemes"]
)

@router.get("/gemini-recommend", summary="Gemini-Powered Scheme Advisor")
def gemini_scheme_recommend(
    user_state: str = Query(..., description="State name (e.g., Maharashtra)"),
    user_district: str = Query(..., description="District name (e.g., Solapur)"),
    user_crop: str = Query(..., description="Crop name (e.g., Onion)"),
    user_land_size: str = Query(..., description="Land size in acres (e.g., 1.5)"),
    user_soil_type: str = Query(..., description="Soil type (e.g., Loamy)"),
    user_category: str = Query(..., description="Farmer category (e.g., General, SC, ST)"),
    user_needs: str = Query(..., description="Comma-separated needs (e.g., irrigation, storage)")
):
    return get_gemini_schemes(
        user_state,
        user_district,
        user_crop,
        user_land_size,
        user_soil_type,
        user_category,
        user_needs
    )

# ✅ New route: Get all states
@router.get("/states", summary="Get all Indian states")
async def fetch_states():
    return await get_all_states()

# ✅ New route: Get districts by state ID
@router.get("/districts", summary="Get districts by state ID")
async def fetch_districts(state_id: int = Query(..., description="State ID from /states endpoint")):
    return await get_districts_by_state(state_id)
