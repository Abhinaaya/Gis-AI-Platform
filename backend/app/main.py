from fastapi import FastAPI
from app.routes.gis_routes import router as gis_router

app = FastAPI()

@app.get("/")
def home():
    return {"message": "GIS AI Platform Running"}

app.include_router(gis_router)