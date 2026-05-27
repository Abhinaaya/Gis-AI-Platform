from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.gis_routes import router as gis_router

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # later restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route
@app.get("/")
def home():
    return {"message": "GIS AI Backend Running"}

# Include GIS routes
app.include_router(gis_router)