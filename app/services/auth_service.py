import os
import logging
from datetime import datetime, timedelta
from typing import Dict
from fastapi import HTTPException, BackgroundTasks, status, Request
from fastapi.responses import HTMLResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from secrets import token_urlsafe
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from psycopg2 import errors as pg_errors

# Load environment variables
load_dotenv()

# Import your user schemas and auth logic
from app.schemas.user import User, LoginRequest, ForgotPasswordRequest
from app.models.db import get_db_connection, create_users_table, DATABASE_URL
from app.utils.auth_utils import hash_password, verify_password

# Setup logging
logger = logging.getLogger("Vavastapak")
logging.basicConfig(level=logging.INFO)

# Ensure users table exists
create_users_table()

# ---------- Mail Configuration ----------
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
)

# ---------- Email Function ----------
async def send_email(subject: str, email_to: str, body: str, is_html: bool = False):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        subtype="html" if is_html else "plain",
    )
    fm = FastMail(conf)
    await fm.send_message(message)

# ---------- Reset Token Storage ----------
reset_tokens: Dict[str, Dict[str, any]] = {}

# ---------- Password Reset Form Rendering ----------
templates = Jinja2Templates(directory="templates")

def show_reset_form(request: Request, token: str):
    for email, token_data in reset_tokens.items():
        if token_data["token"] == token:
            if token_data["expires"] < datetime.utcnow():
                reset_tokens.pop(email, None)
                return templates.TemplateResponse("token_expired.html", {"request": request})
            return templates.TemplateResponse("reset.html", {"request": request, "token": token})
    return templates.TemplateResponse("token_expired.html", {"request": request})

# ---------- Reset Password Model ----------
from pydantic import BaseModel
class ResetPasswordPayload(BaseModel):
    token: str
    new_password: str
    confirm_password: str

# Utility to mask DB URL
def mask_db_url(db_url: str) -> str:
    if not db_url or "@" not in db_url:
        return db_url
    try:
        prefix, rest = db_url.split("//", 1)
        creds, rest = rest.split("@", 1)
        user = creds.split(":")[0]
        return f"{prefix}//{user}:*****@{rest}"
    except:
        return db_url

# ================== USER REGISTRATION ===================
def register(user: User):
    hashed_password = hash_password(user.password)
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (name, email, password, mobile, role) VALUES (%s, %s, %s, %s, %s)",
                    (user.name, user.email, hashed_password, user.mobile, user.role)
                )
                conn.commit()
        return {"message": "User registered successfully"}
    except pg_errors.UniqueViolation as e:
        error_msg = str(e)
        if "email" in error_msg.lower():
            raise HTTPException(status_code=400, detail="Email already exists")
        elif "mobile" in error_msg.lower():
            raise HTTPException(status_code=400, detail="Mobile number already exists")
        else:
            raise HTTPException(status_code=400, detail="User already exists")
    except Exception as e:
        logger.error(f"PostgreSQL Error during registration: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ================== LOGIN ===================
def login(login_request: LoginRequest):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE email=%s", (login_request.email,))
            user = cursor.fetchone()

    if user is None or not verify_password(login_request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"message": "Login successful", "name": user["name"], "role": user["role"]}

# ================== FORGOT PASSWORD ===================
async def forgot_password(payload: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email=%s", (payload.email,))
            user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = token_urlsafe(32)
    expiry = datetime.utcnow() + timedelta(minutes=10)
    reset_tokens[payload.email] = {"token": token, "expires": expiry}

    reset_link = f"https://auth-setup-3v60.onrender.com/reset-password?token={token}"

    subject = "Reset Your Password"
    body = f"""
    Hello,\n\nClick the link below to reset your password (valid for 10 minutes):\n\n{reset_link}\n\nIf you did not request this, ignore this email.\n\n— Vavastapak Team
    """

    background_tasks.add_task(send_email, subject=subject, email_to=payload.email, body=body, is_html=False)

    return {"message": f"Password reset link sent to {payload.email}."}

# ================== RESET PASSWORD ===================
def reset_password(payload: ResetPasswordPayload):
    user_email = None
    for email, token_data in reset_tokens.items():
        if token_data["token"] == payload.token:
            if token_data["expires"] < datetime.utcnow():
                reset_tokens.pop(email, None)
                raise HTTPException(status_code=400, detail="Token has expired")
            user_email = email
            break

    if not user_email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    try:
        hashed_password = hash_password(payload.new_password)
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE users SET password=%s WHERE email=%s", (hashed_password, user_email))
                conn.commit()
        reset_tokens.pop(user_email, None)
        return {"message": "✅ Password successfully reset. You can now log in."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating password: {str(e)}")

# ================== TESTING ENDPOINTS ===================
def get_all_users():
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT id, name, email, mobile, role FROM users")
                users = cursor.fetchall()
        return {"users": users}
    except Exception as e:
        logger.error(f"DB error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def delete_all_users():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM users")
                conn.commit()
        return {"message": "All users deleted successfully"}
    except Exception as e:
        logger.error(f"DB error deleting users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def ping():
    try:
        with get_db_connection() as conn:
            return {"status": "✅ Database connected", "db_url": mask_db_url(DATABASE_URL)}
    except Exception as e:
        return {"status": "❌ Failed to connect", "error": str(e)}

# Print DB URL for debugging
print("\U0001F50D DB URL used:", mask_db_url(DATABASE_URL))
