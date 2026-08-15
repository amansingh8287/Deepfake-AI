from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import detection, health, history, reports
from app.config import get_settings
from app.database import Base, engine

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="1.0.0", openapi_url=f"{settings.api_prefix}/openapi.json")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(detection.router, prefix=settings.api_prefix)
app.include_router(history.router, prefix=settings.api_prefix)
app.include_router(reports.router, prefix=settings.api_prefix)

