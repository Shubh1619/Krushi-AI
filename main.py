from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ✅ CORS import
from app.models import db
from app.routers import crop
from app.routers import mandi
from app.routers import auth
from app.routers import question
from app.routers import weather
from app.routers import schemes
from app.routers import recommendation_engine
from app.routers import calendar
from app.routers import finance 
from app.routers import chat  



app = FastAPI(title="Krushi AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(crop.router, prefix="/crop", tags=["Crop Diagnosis"])
app.include_router(mandi.router)
app.include_router(weather.router)
app.include_router(recommendation_engine.router , tags=["Recommend Fertilizer"])
app.include_router(schemes.router)
app.include_router(question.router, prefix="/question", tags=["Expert Q&A"])
app.include_router(calendar.router)
app.include_router(finance.router)  
app.include_router(chat.router) 


@app.on_event("startup")
def on_startup():
    db.init_db()