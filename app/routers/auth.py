from fastapi import APIRouter, Request, BackgroundTasks, status
from fastapi.responses import HTMLResponse
from app.services import auth_service
from app.schemas.user import User, LoginRequest, ForgotPasswordRequest
from app.services.auth_service import ResetPasswordPayload

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: User):
    return auth_service.register(user)

@router.post("/login")
def login(login_request: LoginRequest):
    return auth_service.login(login_request)

@router.post("/forgot-password/")
async def forgot_password(payload: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    return await auth_service.forgot_password(payload, background_tasks)

@router.get("/reset-password", response_class=HTMLResponse)
async def show_reset_form(request: Request, token: str):
    return auth_service.show_reset_form(request, token)

@router.post("/reset-password/", status_code=status.HTTP_200_OK)
async def reset_password(payload: ResetPasswordPayload):
    return auth_service.reset_password(payload)

@router.get("/users")
def get_all_users():
    return auth_service.get_all_users()

@router.delete("/users/delete-all")
def delete_all_users():
    return auth_service.delete_all_users()

@router.get("/ping")
def ping():
    return auth_service.ping()
