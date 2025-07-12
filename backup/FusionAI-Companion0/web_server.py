"""
FusionAI Companion Web API Server
Provides REST API endpoints for all FusionAI functionality
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import uvicorn
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Import our core components
from core_agent.agent_manager import AgentManager
from ingest.embedding_service import EmbeddingService
from vtuber.avatar_controller import AvatarController
from workflows.workflow_manager import WorkflowManager

logger = logging.getLogger(__name__)


# Pydantic models for API
class CodeGenerationRequest(BaseModel):
    prompt: str
    language: str = "python"
    context: Optional[Dict[str, Any]] = None


class CodeReviewRequest(BaseModel):
    code: str
    language: str = "python"


class CodeFixRequest(BaseModel):
    code: str
    error_message: str
    language: str = "python"


class DocumentationRequest(BaseModel):
    code: str
    language: str = "python"


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class EmbedTextRequest(BaseModel):
    text: str


class EmbedURLRequest(BaseModel):
    url: str
    metadata: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    threshold: float = 0.7


class SpeechRequest(BaseModel):
    text: str
    expression: str = "happy"


class ExpressionRequest(BaseModel):
    expression: str


class AnimationRequest(BaseModel):
    animation_name: str


class WorkflowExecuteRequest(BaseModel):
    workflow_id: str
    input_data: Optional[Dict[str, Any]] = None


class WebhookTriggerRequest(BaseModel):
    webhook_id: str
    data: Dict[str, Any]


class FusionAIWebServer:
    """FastAPI web server for FusionAI Companion"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.app = FastAPI(
            title="FusionAI Companion API",
            description="Unified AI companion system API",
            version="1.0.0",
        )

        # Components
        self.agent_manager = None
        self.embedding_service = None
        self.avatar_controller = None
        self.workflow_manager = None

        # Setup middleware and routes
        self._setup_middleware()
        self._setup_routes()

    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        # CORS
        if self.config.get("cors_enabled", True):
            origins = self.config.get("cors_origins", ["*"])
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

    def _setup_routes(self):
        """Setup API routes"""

        # Health check
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            services = {}

            if self.agent_manager:
                services["agent_manager"] = await self.agent_manager.health_check()
            if self.embedding_service:
                services["embedding_service"] = (
                    await self.embedding_service.health_check()
                )
            if self.avatar_controller:
                services["avatar_controller"] = (
                    await self.avatar_controller.health_check()
                )
            if self.workflow_manager:
                services["workflow_manager"] = (
                    await self.workflow_manager.health_check()
                )

            return {"status": "healthy", "services": services}

        # Agent endpoints
        @self.app.post("/api/agent/generate-code")
        async def generate_code(request: CodeGenerationRequest):
            """Generate code based on prompt"""
            if not self.agent_manager:
                raise HTTPException(
                    status_code=503, detail="Agent manager not available"
                )

            result = await self.agent_manager.generate_code(
                request.prompt, request.language, request.context
            )
            return result

        @self.app.post("/api/agent/review-code")
        async def review_code(request: CodeReviewRequest):
            """Review code and provide suggestions"""
            if not self.agent_manager:
                raise HTTPException(
                    status_code=503, detail="Agent manager not available"
                )

            result = await self.agent_manager.review_code(
                request.code, request.language
            )
            return result

        @self.app.post("/api/agent/fix-code")
        async def fix_code(request: CodeFixRequest):
            """Fix code based on error message"""
            if not self.agent_manager:
                raise HTTPException(
                    status_code=503, detail="Agent manager not available"
                )

            result = await self.agent_manager.fix_code(
                request.code, request.error_message, request.language
            )
            return result

        @self.app.post("/api/agent/generate-docs")
        async def generate_documentation(request: DocumentationRequest):
            """Generate documentation for code"""
            if not self.agent_manager:
                raise HTTPException(
                    status_code=503, detail="Agent manager not available"
                )

            result = await self.agent_manager.generate_documentation(
                request.code, request.language
            )
            return result

        @self.app.post("/api/agent/chat")
        async def chat(request: ChatRequest):
            """Chat with the AI agent"""
            if not self.agent_manager:
                raise HTTPException(
                    status_code=503, detail="Agent manager not available"
                )

            response = await self.agent_manager.chat(request.message, request.context)
            return {"response": response}

        @self.app.get("/api/agent/history")
        async def get_conversation_history(limit: Optional[int] = None):
            """Get conversation history"""
            if not self.agent_manager:
                raise HTTPException(
                    status_code=503, detail="Agent manager not available"
                )

            history = self.agent_manager.get_conversation_history(limit)
            return {"history": history}

        @self.app.delete("/api/agent/history")
        async def clear_conversation_history():
            """Clear conversation history"""
            if not self.agent_manager:
                raise HTTPException(
                    status_code=503, detail="Agent manager not available"
                )

            self.agent_manager.clear_conversation_history()
            return {"message": "History cleared"}

        # Embedding endpoints
        @self.app.post("/api/embed/text")
        async def embed_text(request: EmbedTextRequest):
            """Generate embedding for text"""
            if not self.embedding_service:
                raise HTTPException(
                    status_code=503, detail="Embedding service not available"
                )

            embedding = await self.embedding_service.embed_text(request.text)
            return {"embedding": embedding}

        @self.app.post("/api/embed/url")
        async def embed_url(request: EmbedURLRequest):
            """Crawl and embed URL content"""
            if not self.embedding_service:
                raise HTTPException(
                    status_code=503, detail="Embedding service not available"
                )

            result = await self.embedding_service.crawl_and_embed(
                request.url, request.metadata
            )
            return result

        @self.app.post("/api/embed/search")
        async def search_similar(request: SearchRequest):
            """Search for similar content"""
            if not self.embedding_service:
                raise HTTPException(
                    status_code=503, detail="Embedding service not available"
                )

            results = await self.embedding_service.search_similar(
                request.query, request.limit, request.threshold
            )
            return {"results": results}

        @self.app.get("/api/embed/stats")
        async def get_embedding_stats():
            """Get embedding service statistics"""
            if not self.embedding_service:
                raise HTTPException(
                    status_code=503, detail="Embedding service not available"
                )

            stats = self.embedding_service.get_embedding_stats()
            return stats

        # VTuber endpoints
        @self.app.post("/api/avatar/speak")
        async def avatar_speak(request: SpeechRequest):
            """Make avatar speak"""
            if not self.avatar_controller:
                raise HTTPException(
                    status_code=503, detail="Avatar controller not available"
                )

            success = await self.avatar_controller.speak(
                request.text, request.expression
            )
            return {"success": success}

        @self.app.post("/api/avatar/expression")
        async def set_expression(request: ExpressionRequest):
            """Set avatar expression"""
            if not self.avatar_controller:
                raise HTTPException(
                    status_code=503, detail="Avatar controller not available"
                )

            success = await self.avatar_controller.set_expression(request.expression)
            return {"success": success}

        @self.app.post("/api/avatar/animation")
        async def play_animation(request: AnimationRequest):
            """Play avatar animation"""
            if not self.avatar_controller:
                raise HTTPException(
                    status_code=503, detail="Avatar controller not available"
                )

            success = await self.avatar_controller.play_animation(
                request.animation_name
            )
            return {"success": success}

        @self.app.get("/api/avatar/status")
        async def get_avatar_status():
            """Get avatar status"""
            if not self.avatar_controller:
                raise HTTPException(
                    status_code=503, detail="Avatar controller not available"
                )

            status = self.avatar_controller.get_avatar_status()
            return status

        @self.app.post("/api/avatar/streaming/start")
        async def start_streaming(platform: str = "obs"):
            """Start avatar streaming"""
            if not self.avatar_controller:
                raise HTTPException(
                    status_code=503, detail="Avatar controller not available"
                )

            success = await self.avatar_controller.start_streaming(platform)
            return {"success": success}

        @self.app.post("/api/avatar/streaming/stop")
        async def stop_streaming():
            """Stop avatar streaming"""
            if not self.avatar_controller:
                raise HTTPException(
                    status_code=503, detail="Avatar controller not available"
                )

            success = await self.avatar_controller.stop_streaming()
            return {"success": success}

        # Workflow endpoints
        @self.app.post("/api/workflows/execute")
        async def execute_workflow(request: WorkflowExecuteRequest):
            """Execute a workflow"""
            if not self.workflow_manager:
                raise HTTPException(
                    status_code=503, detail="Workflow manager not available"
                )

            result = await self.workflow_manager.execute_workflow(
                request.workflow_id, request.input_data
            )
            return result

        @self.app.get("/api/workflows")
        async def list_workflows():
            """List all workflows"""
            if not self.workflow_manager:
                raise HTTPException(
                    status_code=503, detail="Workflow manager not available"
                )

            workflows = await self.workflow_manager.list_workflows()
            return {"workflows": workflows}

        @self.app.get("/api/workflows/{workflow_id}/status")
        async def get_workflow_status(workflow_id: str):
            """Get workflow status"""
            if not self.workflow_manager:
                raise HTTPException(
                    status_code=503, detail="Workflow manager not available"
                )

            status = await self.workflow_manager.get_workflow_status(workflow_id)
            return status

        @self.app.post("/api/workflows/{workflow_id}/start")
        async def start_workflow(workflow_id: str):
            """Start a workflow"""
            if not self.workflow_manager:
                raise HTTPException(
                    status_code=503, detail="Workflow manager not available"
                )

            success = await self.workflow_manager.start_workflow(workflow_id)
            return {"success": success}

        @self.app.post("/api/workflows/{workflow_id}/stop")
        async def stop_workflow(workflow_id: str):
            """Stop a workflow"""
            if not self.workflow_manager:
                raise HTTPException(
                    status_code=503, detail="Workflow manager not available"
                )

            success = await self.workflow_manager.stop_workflow(workflow_id)
            return {"success": success}

        @self.app.post("/api/workflows/webhook")
        async def trigger_webhook(request: WebhookTriggerRequest):
            """Trigger webhook workflow"""
            if not self.workflow_manager:
                raise HTTPException(
                    status_code=503, detail="Workflow manager not available"
                )

            result = await self.workflow_manager.trigger_webhook_workflow(
                request.webhook_id, request.data
            )
            return result

        @self.app.get("/api/workflows/history")
        async def get_workflow_history(limit: Optional[int] = None):
            """Get workflow execution history"""
            if not self.workflow_manager:
                raise HTTPException(
                    status_code=503, detail="Workflow manager not available"
                )

            history = self.workflow_manager.get_workflow_history(limit)
            return {"history": history}

        # File upload endpoint
        @self.app.post("/api/upload")
        async def upload_file(file: UploadFile = File(...)):
            """Upload a file for processing"""
            try:
                # Create uploads directory if it doesn't exist
                upload_dir = Path("uploads")
                upload_dir.mkdir(exist_ok=True)

                # Save the file
                file_path = upload_dir / file.filename
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)

                return {
                    "success": True,
                    "filename": file.filename,
                    "size": len(content),
                    "path": str(file_path),
                }

            except Exception as e:
                logger.error(f"File upload error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # Static files
        static_dir = self.config.get("static_files", "static")
        if os.path.exists(static_dir):
            self.app.mount("/static", StaticFiles(directory=static_dir), name="static")

        # Root endpoint
        @self.app.get("/", response_class=HTMLResponse)
        async def root():
            """Root endpoint with basic UI"""
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>FusionAI Companion</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .endpoint { margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 5px; }
                    h1 { color: #333; }
                    h2 { color: #666; }
                    code { background: #e0e0e0; padding: 2px 4px; border-radius: 3px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>FusionAI Companion API</h1>
                    <p>Welcome to the FusionAI Companion API server!</p>

                    <h2>Available Endpoints:</h2>

                    <div class="endpoint">
                        <h3>Health Check</h3>
                        <p><code>GET /health</code> - Check system health</p>
                    </div>

                    <div class="endpoint">
                        <h3>AI Agent</h3>
                        <p><code>POST /api/agent/generate-code</code> - Generate code</p>
                        <p><code>POST /api/agent/review-code</code> - Review code</p>
                        <p><code>POST /api/agent/chat</code> - Chat with AI</p>
                    </div>

                    <div class="endpoint">
                        <h3>Embedding Service</h3>
                        <p><code>POST /api/embed/text</code> - Embed text</p>
                        <p><code>POST /api/embed/url</code> - Crawl and embed URL</p>
                        <p><code>POST /api/embed/search</code> - Search similar content</p>
                    </div>

                    <div class="endpoint">
                        <h3>VTuber Avatar</h3>
                        <p><code>POST /api/avatar/speak</code> - Make avatar speak</p>
                        <p><code>POST /api/avatar/expression</code> - Set expression</p>
                        <p><code>GET /api/avatar/status</code> - Get avatar status</p>
                    </div>

                    <div class="endpoint">
                        <h3>Workflows</h3>
                        <p><code>GET /api/workflows</code> - List workflows</p>
                        <p><code>POST /api/workflows/execute</code> - Execute workflow</p>
                        <p><code>POST /api/workflows/webhook</code> - Trigger webhook</p>
                    </div>

                    <p><a href="/docs">View Interactive API Documentation</a></p>
                </div>
            </body>
            </html>
            """

    async def initialize_components(self, components: Dict[str, Any]):
        """Initialize FusionAI components"""
        self.agent_manager = components.get("agent_manager")
        self.embedding_service = components.get("embedding_service")
        self.avatar_controller = components.get("avatar_controller")
        self.workflow_manager = components.get("workflow_manager")

    async def run(self, host: str = "0.0.0.0", port: int = 8888):
        """Run the web server asynchronously"""
        config = uvicorn.Config(self.app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
