"""
GarvisNeuralMind v2 - Community-Driven AI Companion
Main application entry point with FastAPI and community features.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from src.core.config import get_settings
from src.core.database import init_db
from src.api.v1.router import api_router
from src.community.manager import CommunityManager
from src.community.websocket import WebSocketManager
from src.community.discord_bot import DiscordBot


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global managers
community_manager = CommunityManager()
websocket_manager = WebSocketManager()
discord_bot = DiscordBot()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("🚀 Starting GarvisNeuralMind Community System...")
    
    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")
    
    # Start community manager
    await community_manager.start()
    logger.info("✅ Community manager started")
    
    # Start Discord bot (if enabled)
    settings = get_settings()
    if settings.DISCORD_BOT_TOKEN:
        await discord_bot.start()
        logger.info("✅ Discord bot started")
    
    logger.info("🌟 GarvisNeuralMind is ready for community interactions!")
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down GarvisNeuralMind...")
    await community_manager.stop()
    await discord_bot.stop()
    logger.info("✅ Graceful shutdown completed")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="GarvisNeuralMind Community",
        description="AI-alapú community companion rendszer",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
        debug=settings.DEBUG
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Static files for community UI
    static_path = Path(__file__).parent.parent / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=static_path), name="static")
    
    # WebSocket endpoint for real-time community features
    @app.websocket("/ws/community/{user_id}")
    async def community_websocket(websocket: WebSocket, user_id: str):
        """WebSocket endpoint for community real-time features."""
        await websocket_manager.connect(websocket, user_id)
        try:
            while True:
                data = await websocket.receive_json()
                await websocket_manager.handle_message(user_id, data)
        except WebSocketDisconnect:
            websocket_manager.disconnect(user_id)
    
    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "GarvisNeuralMind Community",
            "version": "2.0.0",
            "community_features": {
                "users_online": len(websocket_manager.active_connections),
                "community_health": await community_manager.get_health_status()
            }
        }
    
    # Community status endpoint
    @app.get("/community/status")
    async def community_status():
        """Get community status and statistics."""
        return await community_manager.get_community_stats()
    
    return app


app = create_app()


async def main():
    """Main entry point for development server."""
    settings = get_settings()
    
    config = uvicorn.Config(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True
    )
    
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())