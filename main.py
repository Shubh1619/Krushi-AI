from fastapi import FastAPI
from app.routers import crop
from app.routers import mandi
from app.routers import auth
from app.routers import forum
from app.routers import locator
from app.routers import weather
from app.routers import notifications
from app.routers import tools
from app.routers import schemes
from app.routers import recommendation_engine


app = FastAPI(title="Crop Disease Detection via Groq")
app.include_router(crop.router, prefix="/crop", tags=["Crop Diagnosis"])
app.include_router(mandi.router)
app.include_router(weather.router)
app.include_router(recommendation_engine.router)

@app.get("/")
def root():
    return {"routes": [route.path for route in app.routes]}

