# GarvisNeuralMind Component Guide

## Overview

This guide provides detailed documentation for all core components in the GarvisNeuralMind system, including their architecture, usage patterns, and integration methods.

## Table of Contents

1. [Core System Components](#core-system-components)
2. [AI Model Components](#ai-model-components)
3. [Memory & Storage Components](#memory--storage-components)
4. [Voice Processing Components](#voice-processing-components)
5. [Integration Components](#integration-components)
6. [Utility Components](#utility-components)
7. [Component Lifecycle](#component-lifecycle)
8. [Advanced Configuration](#advanced-configuration)

---

## Core System Components

### GarvisCore

The central orchestrator that manages all system components and provides the main API interface.

#### Architecture

```python
class GarvisCore:
    """
    Main system orchestrator for GarvisNeuralMind.
    
    Responsibilities:
    - Initialize and manage all subsystems
    - Provide unified API interface
    - Handle system lifecycle
    - Coordinate cross-component communication
    """
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config = self._load_config(config_path)
        self.model_manager = None
        self.memory_manager = None
        self.voice_processor = None
        self.integrations = {}
        self._running = False
        
    def start(self) -> None:
        """Initialize and start all system components."""
        self._initialize_logging()
        self._start_model_manager()
        self._start_memory_manager()
        self._start_voice_processor()
        self._start_integrations()
        self._start_web_server()
        self._running = True
        
    def stop(self) -> None:
        """Gracefully shutdown all components."""
        self._stop_web_server()
        self._stop_integrations()
        self._stop_voice_processor()
        self._stop_memory_manager()
        self._stop_model_manager()
        self._running = False
```

#### Usage Examples

```python
# Basic initialization
garvis = GarvisCore()
garvis.start()

# Custom configuration
garvis = GarvisCore("custom_config.yaml")
garvis.start()

# Check system status
status = garvis.get_status()
print(f"System is {'running' if status['status'] == 'healthy' else 'not healthy'}")

# Process messages
response = garvis.chat("Hello, how can you help me today?")
print(response)

# Graceful shutdown
garvis.stop()
```

#### Configuration

```yaml
core:
  host: "0.0.0.0"
  port: 8000
  debug: false
  log_level: "INFO"
  max_concurrent_requests: 100
  request_timeout: 30
  health_check_interval: 60
```

### WebAPI

REST and WebSocket API server built on FastAPI.

#### Features

- **REST API**: Standard HTTP endpoints for all operations
- **WebSocket API**: Real-time communication for chat and voice
- **Authentication**: API key and session-based auth
- **Rate Limiting**: Configurable rate limits per endpoint
- **Monitoring**: Built-in metrics and health checks

#### Implementation

```python
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware

class WebAPI:
    def __init__(self, garvis_core: GarvisCore):
        self.app = FastAPI(title="GarvisNeuralMind API")
        self.garvis = garvis_core
        self._setup_middleware()
        self._setup_routes()
        
    def _setup_routes(self):
        # Chat endpoints
        @self.app.post("/api/chat")
        async def chat_endpoint(request: ChatRequest):
            return await self._handle_chat(request)
            
        # WebSocket endpoint
        @self.app.websocket("/ws/chat")
        async def websocket_endpoint(websocket: WebSocket):
            await self._handle_websocket(websocket)
```

#### Custom Middleware

```python
class AuthenticationMiddleware:
    """Handle API key authentication."""
    
    def __init__(self, app, api_keys: List[str]):
        self.app = app
        self.api_keys = set(api_keys)
        
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope["headers"])
            auth_header = headers.get(b"authorization", b"").decode()
            
            if not auth_header.startswith("Bearer "):
                # Return 401 Unauthorized
                pass
                
        await self.app(scope, receive, send)
```

---

## AI Model Components

### ModelManager

Manages AI model lifecycle, loading, and inference operations.

#### Architecture

```python
class ModelManager:
    """
    Manages AI models including loading, unloading, and inference.
    
    Supports multiple backends:
    - Ollama
    - vLLM
    - GPT4All
    - HuggingFace Transformers
    - OpenAI-compatible APIs
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.loaded_models = {}
        self.model_backends = {}
        self.default_model = config.get("default_model")
        
    def load_model(self, model_id: str, backend: str = "auto") -> bool:
        """Load a model with specified backend."""
        try:
            if backend == "ollama":
                model = self._load_ollama_model(model_id)
            elif backend == "vllm":
                model = self._load_vllm_model(model_id)
            elif backend == "gpt4all":
                model = self._load_gpt4all_model(model_id)
            else:
                model = self._auto_load_model(model_id)
                
            self.loaded_models[model_id] = model
            return True
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            return False
```

#### Model Backends

##### Ollama Backend

```python
class OllamaBackend:
    def __init__(self, host: str = "localhost", port: int = 11434):
        self.base_url = f"http://{host}:{port}"
        self.client = ollama.Client(host=self.base_url)
        
    def generate(self, model: str, prompt: str, **kwargs) -> str:
        response = self.client.generate(
            model=model,
            prompt=prompt,
            options=kwargs
        )
        return response['response']
        
    def chat(self, model: str, messages: List[Dict], **kwargs) -> str:
        response = self.client.chat(
            model=model,
            messages=messages,
            options=kwargs
        )
        return response['message']['content']
```

##### vLLM Backend

```python
class VLLMBackend:
    def __init__(self, model_path: str, **kwargs):
        from vllm import LLM, SamplingParams
        self.llm = LLM(model=model_path, **kwargs)
        
    def generate(self, prompts: List[str], **kwargs) -> List[str]:
        sampling_params = SamplingParams(**kwargs)
        outputs = self.llm.generate(prompts, sampling_params)
        return [output.outputs[0].text for output in outputs]
```

#### Usage Examples

```python
# Initialize model manager
model_manager = ModelManager(config['models'])

# Load models
model_manager.load_model("llama-7b", backend="ollama")
model_manager.load_model("codellama-7b", backend="vllm")

# Generate text
response = model_manager.generate(
    prompt="Explain quantum computing",
    model_id="llama-7b",
    temperature=0.7,
    max_tokens=500
)

# Chat conversation
messages = [
    {"role": "user", "content": "What is Python?"}
]
response = model_manager.chat(
    messages=messages,
    model_id="llama-7b"
)

# List available models
models = model_manager.list_models()
for model in models:
    print(f"{model['name']}: {model['status']}")
```

### FineTuner

Handles model fine-tuning operations with support for various training strategies.

#### Features

- **LoRA Fine-tuning**: Parameter-efficient fine-tuning
- **Full Fine-tuning**: Complete model parameter updates
- **NEAT Evolution**: Evolutionary optimization for model architecture
- **Multi-GPU Support**: Distributed training capabilities
- **Monitoring**: Real-time training metrics

#### Implementation

```python
class FineTuner:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_jobs = {}
        self.job_queue = Queue()
        self.worker_threads = []
        
    def start_job(self, job_config: Dict[str, Any]) -> str:
        """Start a new fine-tuning job."""
        job_id = str(uuid.uuid4())
        
        job = FineTuningJob(
            job_id=job_id,
            config=job_config,
            status="queued"
        )
        
        self.active_jobs[job_id] = job
        self.job_queue.put(job)
        
        return job_id
        
    def _process_job(self, job: FineTuningJob):
        """Process a fine-tuning job."""
        try:
            job.status = "running"
            
            # Load base model
            model = self._load_base_model(job.config['base_model'])
            
            # Prepare training data
            train_data = self._prepare_training_data(job.config['training_data'])
            
            # Configure training
            if job.config.get('method') == 'lora':
                trainer = LoRATrainer(model, job.config)
            else:
                trainer = FullTrainer(model, job.config)
                
            # Start training with callbacks
            trainer.train(
                train_data,
                callbacks=[
                    ProgressCallback(job),
                    MetricsCallback(job),
                    CheckpointCallback(job)
                ]
            )
            
            job.status = "completed"
            
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
```

#### Training Strategies

##### LoRA (Low-Rank Adaptation)

```python
class LoRATrainer:
    def __init__(self, model, config):
        self.model = model
        self.config = config
        self.lora_config = LoRAConfig(
            r=config.get('lora_r', 16),
            lora_alpha=config.get('lora_alpha', 32),
            target_modules=config.get('target_modules', ["q_proj", "v_proj"]),
            lora_dropout=config.get('lora_dropout', 0.1)
        )
        
    def train(self, train_data, callbacks=None):
        # Apply LoRA to model
        model = get_peft_model(self.model, self.lora_config)
        
        # Setup training arguments
        training_args = TrainingArguments(
            output_dir=self.config['output_dir'],
            learning_rate=self.config.get('learning_rate', 1e-4),
            per_device_train_batch_size=self.config.get('batch_size', 4),
            num_train_epochs=self.config.get('epochs', 3),
            save_steps=500,
            logging_steps=10
        )
        
        # Create trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_data,
            callbacks=callbacks
        )
        
        # Start training
        trainer.train()
```

---

## Memory & Storage Components

### MemoryManager

Manages persistent and working memory for the AI system.

#### Architecture

```python
class MemoryManager:
    """
    Multi-backend memory management system.
    
    Backends:
    - Vector databases (Pinecone, Chroma, FAISS)
    - Key-value stores (Redis, DynamoDB)
    - Relational databases (PostgreSQL, SQLite)
    - Graph databases (Neo4j)
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.backends = {}
        self.embeddings = None
        self._initialize_backends()
        
    def _initialize_backends(self):
        for backend_name, backend_config in self.config['backends'].items():
            if backend_name == "pinecone":
                self.backends[backend_name] = PineconeStorage(backend_config)
            elif backend_name == "redis":
                self.backends[backend_name] = RedisStorage(backend_config)
            elif backend_name == "postgresql":
                self.backends[backend_name] = PostgreSQLStorage(backend_config)
```

#### Storage Backends

##### Vector Storage (Pinecone)

```python
class PineconeStorage:
    def __init__(self, config: Dict[str, Any]):
        import pinecone
        
        pinecone.init(
            api_key=config['api_key'],
            environment=config['environment']
        )
        
        self.index = pinecone.Index(config['index_name'])
        
    def store_embedding(self, vector: List[float], metadata: Dict[str, Any]) -> str:
        """Store vector with metadata."""
        vector_id = str(uuid.uuid4())
        
        self.index.upsert(
            vectors=[(vector_id, vector, metadata)]
        )
        
        return vector_id
        
    def search_similar(self, query_vector: List[float], top_k: int = 10, 
                      filter_dict: Dict = None) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            filter=filter_dict,
            include_metadata=True
        )
        
        return [
            {
                'id': match.id,
                'score': match.score,
                'metadata': match.metadata
            }
            for match in results.matches
        ]
```

##### Cache Storage (Redis)

```python
class RedisStorage:
    def __init__(self, config: Dict[str, Any]):
        import redis
        
        self.client = redis.Redis(
            host=config['host'],
            port=config['port'],
            db=config['db'],
            decode_responses=True
        )
        
    def set_cache(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Store data with TTL."""
        try:
            serialized_value = json.dumps(value)
            return self.client.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Redis cache error: {e}")
            return False
            
    def get_cache(self, key: str) -> Any:
        """Retrieve cached data."""
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Redis retrieval error: {e}")
            return None
```

#### Memory Operations

```python
# Store long-term memory
memory_id = memory_manager.store(
    content="User prefers detailed technical explanations",
    metadata={
        "type": "preference",
        "user_id": "user_123",
        "importance": 8,
        "tags": ["communication_style", "technical"]
    }
)

# Search memories
results = memory_manager.search(
    query="user communication preferences",
    filters={"user_id": "user_123"},
    limit=5
)

# Store conversation cache
memory_manager.cache_conversation(
    session_id="session_456",
    messages=[
        {"role": "user", "content": "What is machine learning?"},
        {"role": "assistant", "content": "Machine learning is..."}
    ],
    ttl=3600  # 1 hour
)
```

---

## Voice Processing Components

### VoiceProcessor

Handles speech-to-text, text-to-speech, and voice activity detection.

#### Architecture

```python
class VoiceProcessor:
    """
    Voice processing system with multiple engine support.
    
    STT Engines:
    - OpenAI Whisper
    - Google Speech-to-Text
    - Azure Speech Services
    - Local models (wav2vec2)
    
    TTS Engines:
    - ElevenLabs
    - Azure TTS
    - Google TTS
    - Local models (Coqui TTS)
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.stt_engine = None
        self.tts_engine = None
        self.vad_model = None
        self._initialize_engines()
```

#### Speech-to-Text Implementation

```python
class WhisperSTT:
    def __init__(self, model_size: str = "base"):
        import whisper
        self.model = whisper.load_model(model_size)
        
    def transcribe(self, audio_data: bytes, language: str = None) -> Dict[str, Any]:
        """Transcribe audio to text."""
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.float32)
        
        # Transcribe
        result = self.model.transcribe(
            audio_array,
            language=language,
            word_timestamps=True
        )
        
        return {
            "text": result["text"],
            "language": result["language"],
            "segments": result["segments"],
            "confidence": self._calculate_confidence(result)
        }
        
    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate average confidence from segments."""
        if not result.get("segments"):
            return 0.5
            
        confidences = [seg.get("confidence", 0.5) for seg in result["segments"]]
        return sum(confidences) / len(confidences)
```

#### Text-to-Speech Implementation

```python
class ElevenLabsTTS:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        
    def synthesize(self, text: str, voice_id: str = "default", 
                  settings: Dict = None) -> bytes:
        """Convert text to speech."""
        import requests
        
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": settings or {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        return response.content
```

#### Real-time Voice Processing

```python
class RealTimeVoiceProcessor:
    def __init__(self, voice_processor: VoiceProcessor):
        self.voice_processor = voice_processor
        self.is_recording = False
        self.audio_buffer = []
        
    async def start_voice_session(self, websocket: WebSocket):
        """Handle real-time voice communication."""
        try:
            while True:
                message = await websocket.receive_json()
                
                if message["type"] == "voice_start":
                    await self._start_recording(websocket, message["data"])
                elif message["type"] == "voice_data":
                    await self._process_audio_chunk(websocket, message["data"])
                elif message["type"] == "voice_end":
                    await self._end_recording(websocket)
                    
        except WebSocketDisconnect:
            await self._cleanup_session()
            
    async def _process_audio_chunk(self, websocket: WebSocket, audio_data: Dict):
        """Process incoming audio chunk."""
        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_data["audio"])
        self.audio_buffer.append(audio_bytes)
        
        # Voice Activity Detection
        if self._detect_speech_end():
            # Transcribe accumulated audio
            full_audio = b''.join(self.audio_buffer)
            transcription = self.voice_processor.transcribe(full_audio)
            
            # Generate AI response
            response_text = await self._generate_response(transcription["text"])
            
            # Convert to speech
            response_audio = self.voice_processor.synthesize(response_text)
            
            # Send back to client
            await websocket.send_json({
                "type": "voice_response",
                "data": {
                    "text": response_text,
                    "audio": base64.b64encode(response_audio).decode(),
                    "duration": len(response_audio) / 16000  # Assuming 16kHz
                }
            })
            
            # Clear buffer
            self.audio_buffer.clear()
```

---

## Integration Components

### BrowserController

Automates web browser interactions for web scraping and automation tasks.

#### Implementation

```python
class BrowserController:
    """
    Browser automation using Playwright/Selenium.
    
    Capabilities:
    - Multi-browser support (Chrome, Firefox, Safari)
    - Headless and headed modes
    - Screenshot capture
    - Element interaction
    - JavaScript execution
    - Cookie management
    """
    
    def __init__(self, browser_type: str = "chrome", headless: bool = False):
        self.browser_type = browser_type
        self.headless = headless
        self.browser = None
        self.page = None
        
    async def start(self):
        """Initialize browser instance."""
        from playwright.async_api import async_playwright
        
        self.playwright = await async_playwright().start()
        
        if self.browser_type == "chrome":
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
        elif self.browser_type == "firefox":
            self.browser = await self.playwright.firefox.launch(headless=self.headless)
        else:
            raise ValueError(f"Unsupported browser: {self.browser_type}")
            
        self.page = await self.browser.new_page()
        
    async def navigate(self, url: str, wait_for: str = "load") -> bool:
        """Navigate to URL."""
        try:
            await self.page.goto(url, wait_until=wait_for)
            return True
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False
            
    async def click_element(self, selector: str, timeout: int = 5000) -> bool:
        """Click element by selector."""
        try:
            await self.page.click(selector, timeout=timeout)
            return True
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return False
            
    async def extract_content(self, selector: str = None) -> str:
        """Extract page content."""
        if selector:
            elements = await self.page.query_selector_all(selector)
            content = []
            for element in elements:
                text = await element.inner_text()
                content.append(text)
            return "\n".join(content)
        else:
            return await self.page.content()
```

#### AI-Powered Web Automation

```python
class AIWebAutomator:
    """AI-powered web automation using vision and language models."""
    
    def __init__(self, browser_controller: BrowserController, ai_model):
        self.browser = browser_controller
        self.ai_model = ai_model
        
    async def perform_task(self, instruction: str) -> Dict[str, Any]:
        """Perform web task using natural language instruction."""
        # Take screenshot
        screenshot = await self.browser.page.screenshot()
        
        # Get page structure
        page_structure = await self._extract_page_structure()
        
        # Generate action plan using AI
        prompt = f"""
        Task: {instruction}
        
        Page structure:
        {page_structure}
        
        Generate a step-by-step plan to complete this task.
        Include specific selectors and actions.
        """
        
        plan = await self.ai_model.generate(prompt)
        
        # Execute plan
        results = []
        for step in self._parse_plan(plan):
            result = await self._execute_step(step)
            results.append(result)
            
        return {
            "instruction": instruction,
            "steps_executed": len(results),
            "success": all(r["success"] for r in results),
            "results": results
        }
```

### VSCodeConnector

Integrates with Visual Studio Code for code analysis and generation.

#### Implementation

```python
class VSCodeConnector:
    """
    VSCode integration for code analysis and generation.
    
    Features:
    - File operations
    - Code analysis
    - Extension integration
    - Debug session management
    - Terminal operations
    """
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.extensions = {}
        
    def analyze_codebase(self) -> Dict[str, Any]:
        """Analyze entire codebase structure."""
        analysis = {
            "files": [],
            "languages": set(),
            "dependencies": {},
            "structure": {}
        }
        
        for root, dirs, files in os.walk(self.workspace_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, self.workspace_path)
                
                file_info = {
                    "path": relative_path,
                    "language": self._detect_language(file),
                    "size": os.path.getsize(file_path),
                    "modified": os.path.getmtime(file_path)
                }
                
                analysis["files"].append(file_info)
                analysis["languages"].add(file_info["language"])
                
        return analysis
        
    def generate_code(self, specification: str, file_path: str) -> str:
        """Generate code based on specification."""
        # Analyze existing code context
        context = self._get_file_context(file_path)
        
        # Generate code using AI
        prompt = f"""
        Generate code for the following specification:
        {specification}
        
        Context from existing file:
        {context}
        
        Maintain consistency with existing code style and patterns.
        """
        
        generated_code = self.ai_model.generate(prompt)
        return generated_code
```

---

## Utility Components

### ConfigManager

Handles configuration loading, validation, and hot-reloading.

```python
class ConfigManager:
    """
    Configuration management with validation and hot-reloading.
    """
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = {}
        self.validators = {}
        self.watchers = []
        
    def load_config(self) -> Dict[str, Any]:
        """Load and validate configuration."""
        with open(self.config_path, 'r') as f:
            raw_config = yaml.safe_load(f)
            
        # Environment variable substitution
        resolved_config = self._resolve_env_vars(raw_config)
        
        # Validation
        self._validate_config(resolved_config)
        
        self.config = resolved_config
        return self.config
        
    def _resolve_env_vars(self, config: Any) -> Any:
        """Resolve environment variables in config."""
        if isinstance(config, dict):
            return {k: self._resolve_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._resolve_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            env_var = config[2:-1]
            return os.getenv(env_var, config)
        else:
            return config
```

### Logger

Structured logging with multiple outputs and log levels.

```python
class StructuredLogger:
    """
    Structured logging system with multiple handlers.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("garvis")
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Setup logging handlers."""
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = JsonFormatter()
        console_handler.setFormatter(console_formatter)
        
        # File handler
        file_handler = RotatingFileHandler(
            self.config.get("log_file", "garvis.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(self.config.get("log_level", "INFO"))
```

---

## Component Lifecycle

### Initialization Order

1. **ConfigManager**: Load and validate configuration
2. **Logger**: Initialize logging system
3. **ModelManager**: Load AI models
4. **MemoryManager**: Initialize storage backends
5. **VoiceProcessor**: Setup voice engines
6. **Integrations**: Initialize external connectors
7. **WebAPI**: Start web server

### Health Checks

```python
class HealthChecker:
    def __init__(self, components: Dict[str, Any]):
        self.components = components
        
    async def check_all(self) -> Dict[str, Any]:
        """Check health of all components."""
        results = {}
        
        for name, component in self.components.items():
            try:
                if hasattr(component, 'health_check'):
                    results[name] = await component.health_check()
                else:
                    results[name] = {"status": "unknown"}
            except Exception as e:
                results[name] = {"status": "unhealthy", "error": str(e)}
                
        overall_status = "healthy" if all(
            r.get("status") == "healthy" for r in results.values()
        ) else "unhealthy"
        
        return {
            "overall_status": overall_status,
            "components": results,
            "timestamp": datetime.utcnow().isoformat()
        }
```

### Graceful Shutdown

```python
class ShutdownManager:
    def __init__(self, components: List[Any]):
        self.components = components
        
    async def shutdown(self, timeout: int = 30):
        """Gracefully shutdown all components."""
        logger.info("Starting graceful shutdown...")
        
        # Stop accepting new requests
        await self._stop_accepting_requests()
        
        # Wait for active requests to complete
        await self._wait_for_active_requests(timeout=timeout//2)
        
        # Shutdown components in reverse order
        for component in reversed(self.components):
            try:
                if hasattr(component, 'stop'):
                    await component.stop()
                logger.info(f"Stopped {component.__class__.__name__}")
            except Exception as e:
                logger.error(f"Error stopping {component.__class__.__name__}: {e}")
                
        logger.info("Graceful shutdown completed")
```

---

## Advanced Configuration

### Component-Specific Configuration

```yaml
# Model Manager Configuration
models:
  default_model: "llama-7b"
  model_cache_size: "8GB"
  gpu_acceleration: true
  backends:
    ollama:
      host: "localhost"
      port: 11434
      timeout: 300
    vllm:
      tensor_parallel_size: 2
      gpu_memory_utilization: 0.8
    huggingface:
      cache_dir: "/models/cache"
      device_map: "auto"

# Memory Manager Configuration  
memory:
  default_backend: "hybrid"  # Use multiple backends
  embedding_model: "all-MiniLM-L6-v2"
  embedding_dimension: 384
  backends:
    pinecone:
      api_key: "${PINECONE_API_KEY}"
      environment: "us-west1-gcp"
      index_name: "garvis-memory"
      metadata_config:
        indexed: ["category", "importance", "user_id"]
    redis:
      host: "localhost"
      port: 6379
      db: 0
      max_connections: 20
      ttl_default: 3600
    postgresql:
      connection_string: "${DATABASE_URL}"
      table_name: "conversations"
      connection_pool_size: 10

# Voice Processing Configuration
voice:
  input:
    sample_rate: 16000
    format: "wav"
    chunk_size: 1024
    vad_threshold: 0.5
    language_detection: true
  output:
    voice_model: "elevenlabs"
    default_voice: "21m00Tcm4TlvDq8ikWAM"
    speed: 1.0
    stability: 0.5
  engines:
    stt:
      primary: "whisper"
      fallback: "google"
    tts:
      primary: "elevenlabs"
      fallback: "azure"

# Integration Configuration
integrations:
  browser:
    default_browser: "chrome"
    headless: false
    timeout: 30000
    user_agent: "GarvisNeuralMind/1.0"
    viewport:
      width: 1920
      height: 1080
  vscode:
    workspace_path: "/workspace"
    extensions: ["roo-code", "ui-tars"]
    auto_save: true
  apis:
    openrouter:
      api_key: "${OPENROUTER_API_KEY}"
      base_url: "https://openrouter.ai/api/v1"
      default_model: "deepseek/deepseek-r1"
      timeout: 60
    google_ai:
      api_key: "${GOOGLE_AI_API_KEY}"
      default_model: "gemini-pro"
      safety_settings: "block_few"
```

This comprehensive component guide provides detailed documentation for all major components in the GarvisNeuralMind system. Each component includes architecture details, implementation examples, configuration options, and usage patterns to help developers understand and work with the system effectively.