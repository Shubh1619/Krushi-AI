import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import HTTPException, BackgroundTasks, Request, Depends
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from secrets import token_urlsafe
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from psycopg2 import errors as pg_errors
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

from app.schemas.user import User
from app.models.db import get_db_connection, create_users_table
from app.utils.auth_utils import hash_password, verify_password

# JWT setup
SECRET_KEY = "lz9yTDyLDrDjK5jD3O3eYmErv4QehbJG_6kkU5R_GAk"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

load_dotenv(dotenv_path=".env")

# Logging
logger = logging.getLogger("KRISHI AI")
logging.basicConfig(level=logging.INFO)

# Ensure users table exists
create_users_table()

# Email Config
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

TEMPLATES_DIR = "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)
reset_tokens: Dict[str, Dict[str, Any]] = {}

class ResetPasswordPayload(BaseModel):
    token: str
    new_password: str
    confirm_password: str

def mask_db_url(db_url: str) -> str:
    if not db_url or "@" not in db_url:
        return db_url
    try:
        prefix, rest = db_url.split("//", 1)
        creds, rest = rest.split("@", 1)
        user = creds.split(":")[0]
        return f"{prefix}//{user}:*****@{rest}"
    except Exception:
        return db_url

# ------------------ USERS ------------------

def get_all_users(current_user_id: int) -> list[dict]:
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT id, name FROM users WHERE id != %s", (current_user_id,))
            return cursor.fetchall()

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def register(user: User):
    hashed_password = hash_password(user.password)
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (name, email, password, mobile) VALUES (%s, %s, %s, %s)",
                    (user.name, user.email, hashed_password, user.mobile)
                )
                conn.commit()
        return {"message": "User registered successfully"}
    except pg_errors.UniqueViolation as e:
        msg = str(e)
        if "email" in msg.lower():
            raise HTTPException(status_code=400, detail="Email already exists")
        elif "mobile" in msg.lower():
            raise HTTPException(status_code=400, detail="Mobile number already exists")
        else:
            raise HTTPException(status_code=400, detail="User already exists")
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def login(login_request):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE email=%s", (login_request.email,))
            user = cursor.fetchone()

    if not user or not verify_password(login_request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({
        "id": user["id"],
        "name": user["name"]
    })

    other_users = get_all_users(current_user_id=user["id"])

    return {
        "message": "Login successful",
        "user_id": user["id"],
        "name": user["name"],
        "token": token,
        "users": other_users
    }

# ------------------ JWT Helper ------------------

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



# ------------------ Forgot/Reset Password (same as before) ------------------

async def send_email(subject: str, email_to: str, body: str, is_html: bool = False):
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            body=body,
            subtype="html" if is_html else "plain",
        )
        await FastMail(conf).send_message(message)
        logger.info(f"Email sent to {email_to}")
    except Exception as e:
        logger.error(f"Failed to send email to {email_to}: {e}")

def show_reset_form(request: Request, token: str):
    for email, token_data in reset_tokens.items():
        if token_data["token"] == token:
            if token_data["expires"] < datetime.utcnow():
                reset_tokens.pop(email, None)
                return templates.TemplateResponse("token_expired.html", {"request": request})
            return templates.TemplateResponse("reset.html", {"request": request, "token": token})
    return templates.TemplateResponse("token_expired.html", {"request": request})

async def forgot_password(payload, background_tasks: BackgroundTasks):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email=%s", (payload.email,))
            user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = token_urlsafe(32)
    reset_tokens[payload.email] = {
        "token": token,
        "expires": datetime.utcnow() + timedelta(minutes=10)
    }

    reset_link = f"https://krushi-ai.onrender.com/auth/auth/reset-password?token={token}"
    subject = "🔐 तुमचा पासवर्ड रीसेट करा - Krushi AI"

    body = f"""
प्रिय {user["name"]},

आम्हाला तुमच्या Krushi AI खात्यासाठी पासवर्ड रीसेट करण्याची विनंती मिळाली आहे.

👉 रीसेट लिंक: {reset_link}

ही लिंक १० मिनिटांसाठी वैध आहे.

जर तुम्ही ही विनंती केलेली नसेल, तर कृपया दुर्लक्ष करा.
तुमचे खाते सुरक्षित आहे.

शुभेच्छा,  
Krushi AI टीम
"""

    background_tasks.add_task(send_email, subject=subject, email_to=payload.email, body=body)
    return {"message": f"पासवर्ड रीसेट लिंक {payload.email} वर पाठवली आहे."}

def reset_password(payload: ResetPasswordPayload):
    email = next((e for e, t in reset_tokens.items() if t["token"] == payload.token), None)

    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    token_data = reset_tokens[email]
    if token_data["expires"] < datetime.utcnow():
        reset_tokens.pop(email, None)
        raise HTTPException(status_code=400, detail="Token has expired")

    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    try:
        hashed = hash_password(payload.new_password)
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE users SET password=%s WHERE email=%s", (hashed, email))
                conn.commit()
        reset_tokens.pop(email, None)
        return {"message": "✅ Password successfully reset. You can now log in."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating password: {str(e)}")
