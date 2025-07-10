#!/usr/bin/env python3
"""
FusionAI Companion - Main Application Entry Point
Unified AI companion system with code generation, VTuber, and agent capabilities
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core_agent.agent_manager import AgentManager
from ingest.embedding_service import EmbeddingService
from vtuber.avatar_controller import AvatarController
from web_server import FusionAIWebServer
from workflows.workflow_manager import WorkflowManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/fusionai.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


class FusionAICompanion:
    """Main FusionAI Companion application class"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/main.json"
        self.config = self._load_config()

        # Initialize components
        self.agent_manager = None
        self.embedding_service = None
        self.avatar_controller = None
        self.workflow_manager = None

        # Runtime state
        self.is_running = False
        self.services = {}

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            import json

            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_path} not found, using defaults")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "core_agent": {
                "enabled": True,
                "provider": "ollama",
                "model": "qwen2:7b",
                "max_tokens": 4096,
                "temperature": 0.1,
            },
            "embedding": {
                "enabled": True,
                "model": "nomic-embed-text",
                "chunk_size": 1000,
                "chunk_overlap": 200,
            },
            "vtuber": {
                "enabled": False,
                "model_path": "vtuber/models/default.vrm",
                "voice_enabled": True,
                "animation_enabled": True,
            },
            "workflows": {
                "enabled": True,
                "auto_start": ["health_check", "model_warmup"],
                "n8n_url": "http://localhost:5678",
            },
            "web_ui": {
                "enabled": True,
                "host": "0.0.0.0",
                "port": 8888,
                "cors_enabled": True,
            },
            "monitoring": {
                "enabled": True,
                "langfuse_enabled": True,
                "metrics_interval": 60,
            },
        }

    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing FusionAI Companion...")

        try:
            # Initialize core agent
            if self.config.get("core_agent", {}).get("enabled", True):
                logger.info("Initializing Core Agent...")
                self.agent_manager = AgentManager(self.config["core_agent"])
                await self.agent_manager.initialize()
                self.services["agent_manager"] = self.agent_manager

            # Initialize embedding service
            if self.config.get("embedding", {}).get("enabled", True):
                logger.info("Initializing Embedding Service...")
                self.embedding_service = EmbeddingService(self.config["embedding"])
                await self.embedding_service.initialize()
                self.services["embedding_service"] = self.embedding_service

            # Initialize VTuber controller
            if self.config.get("vtuber", {}).get("enabled", False):
                logger.info("Initializing VTuber Controller...")
                self.avatar_controller = AvatarController(self.config["vtuber"])
                await self.avatar_controller.initialize()
                self.services["avatar_controller"] = self.avatar_controller

            # Initialize workflow manager
            if self.config.get("workflows", {}).get("enabled", True):
                logger.info("Initializing Workflow Manager...")
                self.workflow_manager = WorkflowManager(self.config["workflows"])
                await self.workflow_manager.initialize()
                self.services["workflow_manager"] = self.workflow_manager

            # Initialize web server
            if self.config.get("web_ui", {}).get("enabled", True):
                logger.info("Initializing Web Server...")

                self.web_server = FusionAIWebServer(self.config["web_ui"])
                await self.web_server.initialize_components(self.services)
                self.services["web_server"] = self.web_server

            logger.info("All components initialized successfully!")

        except Exception as e:
            logger.error(f"Error during initialization: {e}")
            raise

    async def start(self):
        """Start all services"""
        if self.is_running:
            logger.warning("FusionAI Companion is already running")
            return

        logger.info("Starting FusionAI Companion...")

        try:
            # Start all services except web server
            for service_name, service in self.services.items():
                if service_name != "web_server" and hasattr(service, "start"):
                    logger.info(f"Starting {service_name}...")
                    await service.start()

            self.is_running = True
            logger.info("FusionAI Companion started successfully!")

            # Start web server (blocking) or main loop
            if "web_server" in self.services:
                web_config = self.config.get("web_ui", {})
                host = web_config.get("host", "0.0.0.0")
                port = web_config.get("port", 8888)

                logger.info(f"Starting web server on {host}:{port}")
                logger.info("Access the web interface at:")
                logger.info(f"  • Main API: http://localhost:{port}")
                logger.info(f"  • API Docs: http://localhost:{port}/docs")

                # Run the web server (this will block)
                await self.services["web_server"].run(host, port)
            else:
                # Start main loop if no web server
                await self._main_loop()

        except Exception as e:
            logger.error(f"Error during startup: {e}")
            await self.stop()
            raise

    async def stop(self):
        """Stop all services"""
        if not self.is_running:
            return

        logger.info("Stopping FusionAI Companion...")

        try:
            # Stop all services in reverse order
            for service_name, service in reversed(list(self.services.items())):
                if hasattr(service, "stop"):
                    logger.info(f"Stopping {service_name}...")
                    await service.stop()

            self.is_running = False
            logger.info("FusionAI Companion stopped successfully!")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    async def _main_loop(self):
        """Main application loop"""
        try:
            while self.is_running:
                # Health check
                await self._health_check()

                # Process any pending tasks
                await self._process_tasks()

                # Sleep before next iteration
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            await self.stop()

    async def _health_check(self):
        """Perform health check on all services"""
        for service_name, service in self.services.items():
            if hasattr(service, "health_check"):
                try:
                    if not await service.health_check():
                        logger.warning(f"Health check failed for {service_name}")
                except Exception as e:
                    logger.error(f"Health check error for {service_name}: {e}")

    async def _process_tasks(self):
        """Process any pending tasks"""
        # This is where we can add background task processing
        pass


def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="FusionAI Companion - Unified AI Agent System"
    )

    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default="config/main.json",
        help="Path to configuration file",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level",
    )

    parser.add_argument(
        "--mode",
        choices=["full", "agent-only", "vtuber-only", "workflow-only"],
        default="full",
        help="Run mode",
    )

    parser.add_argument(
        "--docker", action="store_true", help="Running in Docker container"
    )

    return parser


async def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()

    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Create and start the application
    app = FusionAICompanion(config_path=args.config)

    try:
        await app.initialize()
        await app.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)
    finally:
        await app.stop()


if __name__ == "__main__":
    # Ensure required directories exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # Run the application
    asyncio.run(main())
