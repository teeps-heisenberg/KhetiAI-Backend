"""
Main API router for v1
"""

from fastapi import APIRouter
from app.api.v1.endpoints import health, chat, crop_analysis

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(crop_analysis.router, prefix="/crop-analysis", tags=["crop-analysis"])
