from fastapi import APIRouter, Query
from app.services.scheme_service import get_all_schemes, get_scheme_by_id, get_recommended_schemes, get_gemini_schemes

router = APIRouter(prefix="/schemes", tags=["Government Schemes"])

@router.get("/all")
def list_schemes(state: str = Query(None), crop: str = Query(None)):
    return get_all_schemes(state, crop)

@router.get("/{scheme_id}")
def scheme_details(scheme_id: str):
    return get_scheme_by_id(scheme_id)

@router.get("/recommended")
def recommended_schemes(user_id: str):
    return get_recommended_schemes(user_id)

@router.get("/gemini-recommend")
def gemini_scheme_recommend(
    user_state: str = Query(...),
    user_district: str = Query(...),
    user_crop: str = Query(...),
    user_land_size: str = Query(...),
    user_soil_type: str = Query(...),
    user_category: str = Query(...),
    user_needs: str = Query(...)
):
    """
    Get Gemini-powered government scheme recommendations for a farmer.
    """
    return get_gemini_schemes(user_state, user_district, user_crop, user_land_size, user_soil_type, user_category, user_needs)
