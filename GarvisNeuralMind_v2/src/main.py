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
from src.api.v1.router import api_router
from src.community.discord_bot import DiscordBot
from src.community.manager import CommunityManager
from src.community.websocket import WebSocketManager
from src.core.config import get_settings
from src.core.database import init_db

# Configure logging
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)
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
        debug=settings.DEBUG,
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

    # Static files for community UI and demos
    static_path = Path(__file__).parent.parent / "static"
    static_path.mkdir(exist_ok=True)  # Ensure static directory exists
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

    # WebSocket endpoint for WebRTC signaling (voice communication)
    signaling_clients = {}

    @app.websocket("/ws/signaling/{user_id}")
    async def signaling_websocket(websocket: WebSocket, user_id: str):
        """WebSocket endpoint for WebRTC signaling (SDP/ICE exchange)."""
        await websocket.accept()
        signaling_clients[user_id] = websocket
        try:
            while True:
                message = await websocket.receive_json()
                # Expecting: {"to": "target_user_id", "data": {...}}
                target_id = message.get("to")
                data = message.get("data")
                if target_id and target_id in signaling_clients:
                    await signaling_clients[target_id].send_json(
                        {"from": user_id, "data": data}
                    )
        except WebSocketDisconnect:
            signaling_clients.pop(user_id, None)

    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        users_online = len(websocket_manager.active_connections)
        community_health = await community_manager.get_health_status()
        return {
            "status": "healthy",
            "service": "GarvisNeuralMind Community",
            "version": "2.0.0",
            "community_features": {
                "users_online": users_online,
                "community_health": community_health,
            },
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
        access_log=True,
    )

    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
