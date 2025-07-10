"""
API Router - Main routing for community features.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import List, Optional, Dict, Any

from src.api.v1.endpoints import (
    auth, users, communities, posts, messages, ai_companions
)
from src.core.config import get_settings

settings = get_settings()

# Create main API router
api_router = APIRouter()

# Security scheme
security = HTTPBearer()

# Include endpoint routers
api_router.include_router(
    auth.router, 
    prefix="/auth", 
    tags=["authentication"]
)

api_router.include_router(
    users.router, 
    prefix="/users", 
    tags=["users"]
)

api_router.include_router(
    communities.router, 
    prefix="/communities", 
    tags=["communities"]
)

api_router.include_router(
    posts.router, 
    prefix="/posts", 
    tags=["posts"]
)

api_router.include_router(
    messages.router, 
    prefix="/messages", 
    tags=["messages"]
)

api_router.include_router(
    ai_companions.router, 
    prefix="/ai-companions", 
    tags=["ai-companions"]
)

# Global health check
@api_router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Global API health check."""
    return {
        "status": "healthy",
        "service": "GarvisNeuralMind Community API",
        "version": "2.0.0",
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users", 
            "communities": "/api/v1/communities",
            "posts": "/api/v1/posts",
            "messages": "/api/v1/messages",
            "ai_companions": "/api/v1/ai-companions"
        }
    }

# API info endpoint
@api_router.get("/info", response_model=Dict[str, Any])
async def api_info():
    """Get API information and capabilities."""
    return {
        "name": "GarvisNeuralMind Community API",
        "version": "2.0.0",
        "description": "AI-powered community platform with VTuber integration",
        "features": {
            "user_management": True,
            "community_system": True,
            "real_time_chat": True,
            "ai_companions": True,
            "vtuber_integration": True,
            "discord_bridge": True,
            "plugin_system": True
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "websocket": {
            "community_chat": "/ws/community/{user_id}"
        }
    }