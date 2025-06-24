from fastapi import APIRouter, Query
from app.services.scheme_service import (
    get_all_schemes,
    get_scheme_by_id,
    get_recommended_schemes,
    get_gemini_schemes
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
    """
    🎯 Get government scheme recommendations based on farmer profile 
    using Google Gemini AI.

    Returns schemes with:
    - Name
    - Type
    - Description
    - Eligibility
    - How to apply
    - Application portal
    """
    return get_gemini_schemes(
        user_state,
        user_district,
        user_crop,
        user_land_size,
        user_soil_type,
        user_category,
        user_needs
    )
