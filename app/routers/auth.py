from fastapi import APIRouter, Request, BackgroundTasks, status
from fastapi.responses import HTMLResponse
from app.services import auth_service
from app.schemas.user import User, LoginRequest, ForgotPasswordRequest
from app.services.auth_service import ResetPasswordPayload
from typing import List

router = APIRouter(prefix="/auth", tags=["Authentication"])

# 🚀 Register
@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Register a new user")
def register(user: User):
    return auth_service.register(user)

# 🔐 Login
@router.post("/login", summary="User login")
def login(login_request: LoginRequest):
    return auth_service.login(login_request)

# 📩 Forgot Password (Send Email)
@router.post("/forgot-password", summary="Send password reset email")
async def forgot_password(payload: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    return await auth_service.forgot_password(payload, background_tasks)

# 🔑 Reset Form UI (HTML Page)
@router.get("/reset-password", response_class=HTMLResponse, summary="Render password reset form")
async def show_reset_form(request: Request, token: str):
    return auth_service.show_reset_form(request, token)

# ✅ Submit Reset Password Form
@router.post("/reset-password", status_code=status.HTTP_200_OK, summary="Reset password")
async def reset_password(payload: ResetPasswordPayload):
    return auth_service.reset_password(payload)

