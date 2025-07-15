from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ✅ CORS import

from app.routers import crop
from app.routers import mandi
from app.routers import auth
from app.routers import question
from app.routers import weather
from app.routers import schemes
from app.routers import recommendation_engine
from app.routers import calendar
from app.routers import finance  # Added import

app = FastAPI(title="Krushi AI")

# ✅ Add CORS Middleware (required for Flutter Web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For now, allow all. You can restrict later.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ API Routes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(crop.router, prefix="/crop", tags=["Crop Diagnosis"])
app.include_router(mandi.router)
app.include_router(weather.router)
app.include_router(recommendation_engine.router)
app.include_router(schemes.router)
app.include_router(question.router, prefix="/question", tags=["Expert Q&A"])
app.include_router(calendar.router)
app.include_router(finance.router)  # Register finance router

@app.get("/")
def root():
    return {"routes": [route.path for route in app.routes]}
