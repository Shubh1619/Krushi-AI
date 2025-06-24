from fastapi import APIRouter, Query
from app.services.scheme_service import get_all_schemes, get_scheme_by_id, get_recommended_schemes

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
