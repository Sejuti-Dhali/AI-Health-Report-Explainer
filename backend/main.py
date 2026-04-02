import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="MediScan AI", version="1.0")


def _cors_origins():
    raw = os.getenv("CORS_ORIGINS", "")
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]

    if origins:
        return origins

    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
