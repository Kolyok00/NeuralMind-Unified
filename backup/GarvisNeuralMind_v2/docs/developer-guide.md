# GarvisNeuralMind Developer Guide

## Overview

This guide provides comprehensive documentation for developers working with the GarvisNeuralMind system, including setup, development workflow, testing, and deployment procedures.

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Testing Framework](#testing-framework)
5. [Deployment Guide](#deployment-guide)
6. [Performance Optimization](#performance-optimization)
7. [Troubleshooting](#troubleshooting)
8. [Contributing Guidelines](#contributing-guidelines)

---

## Development Environment Setup

### Prerequisites

```bash
# System requirements
- Python 3.9+
- Docker and Docker Compose
- Node.js 16+ (for web UI)
- CUDA 11.8+ (for GPU acceleration)
- 16GB+ RAM recommended
- 100GB+ storage for models
```

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/your-org/GarvisNeuralMind.git
cd GarvisNeuralMind

# Create virtual environment
python -m venv garvis-env
source garvis-env/bin/activate  # Linux/Mac
# or garvis-env\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Run initial setup
python scripts/setup.py
```

### Docker Development Environment

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  garvis-dev:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app/src
      - /app/src/venv
    ports:
      - "8000:8000"
      - "5678:5678"  # Debug port
    environment:
      - PYTHONPATH=/app/src
      - DEBUG=true
    depends_on:
      - redis
      - postgres
      
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
      
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: garvis_dev
      POSTGRES_USER: garvis
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### IDE Configuration

#### VS Code Settings

```json
{
    "python.defaultInterpreterPath": "./garvis-env/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

---

## Project Structure

```
GarvisNeuralMind/
├── src/
│   ├── garvis/
│   │   ├── core/           # Core system components
│   │   ├── models/         # AI model management
│   │   ├── memory/         # Memory management
│   │   ├── voice/          # Voice processing
│   │   ├── integrations/   # External integrations
│   │   ├── api/            # Web API
│   │   └── utils/          # Utility functions
│   └── main.py
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
├── config/
│   ├── settings.yaml       # Main configuration
│   └── environments/       # Environment-specific configs
├── docs/                   # Documentation
├── scripts/                # Utility scripts
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
└── docker-compose.yml      # Production docker setup
```

### Key Modules

#### Core Module (`src/garvis/core/`)

```python
# core/__init__.py
from .garvis_core import GarvisCore
from .config_manager import ConfigManager
from .logger import StructuredLogger

# core/garvis_core.py
class GarvisCore:
    """Main orchestrator for the GarvisNeuralMind system."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load_config()
        self.logger = StructuredLogger(self.config.get('logging', {}))
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize all system components."""
        # Component initialization logic here
        pass
```

#### API Module (`src/garvis/api/`)

```python
# api/main.py
from fastapi import FastAPI, Depends
from .routes import chat, models, memory, status
from .middleware import AuthMiddleware, LoggingMiddleware

def create_app(garvis_core: GarvisCore) -> FastAPI:
    app = FastAPI(
        title="GarvisNeuralMind API",
        version="1.0.0",
        description="AI Assistant API"
    )
    
    # Add middleware
    app.add_middleware(AuthMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    # Include routers
    app.include_router(chat.router, prefix="/api/chat")
    app.include_router(models.router, prefix="/api/models")
    app.include_router(memory.router, prefix="/api/memory")
    app.include_router(status.router, prefix="/api/status")
    
    return app
```

---

## Development Workflow

### Feature Development

1. **Create Feature Branch**
```bash
git checkout -b feature/new-voice-engine
```

2. **Write Tests First (TDD)**
```python
# tests/unit/voice/test_whisper_engine.py
import pytest
from garvis.voice.engines import WhisperEngine

class TestWhisperEngine:
    def test_transcribe_english_audio(self):
        engine = WhisperEngine()
        audio_data = load_test_audio("hello_world.wav")
        
        result = engine.transcribe(audio_data, language="en")
        
        assert result["text"].lower() == "hello world"
        assert result["confidence"] > 0.8
        
    def test_transcribe_with_timestamps(self):
        engine = WhisperEngine()
        audio_data = load_test_audio("multi_sentence.wav")
        
        result = engine.transcribe(audio_data, word_timestamps=True)
        
        assert len(result["segments"]) > 1
        assert all("start" in seg and "end" in seg for seg in result["segments"])
```

3. **Implement Feature**
```python
# src/garvis/voice/engines/whisper_engine.py
import whisper
import numpy as np
from typing import Dict, Any, Optional

class WhisperEngine:
    def __init__(self, model_size: str = "base"):
        self.model = whisper.load_model(model_size)
        
    def transcribe(self, audio_data: bytes, language: Optional[str] = None, 
                  word_timestamps: bool = False) -> Dict[str, Any]:
        """Transcribe audio to text using Whisper."""
        audio_array = np.frombuffer(audio_data, dtype=np.float32)
        
        result = self.model.transcribe(
            audio_array,
            language=language,
            word_timestamps=word_timestamps
        )
        
        return {
            "text": result["text"],
            "language": result["language"],
            "segments": result.get("segments", []),
            "confidence": self._calculate_confidence(result)
        }
```

4. **Run Tests**
```bash
# Run specific test file
pytest tests/unit/voice/test_whisper_engine.py -v

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/garvis --cov-report=html
```

5. **Integration Testing**
```python
# tests/integration/test_voice_processing.py
import pytest
from garvis.core import GarvisCore
from garvis.voice import VoiceProcessor

@pytest.mark.integration
class TestVoiceProcessingIntegration:
    def test_end_to_end_voice_processing(self):
        garvis = GarvisCore("config/test_settings.yaml")
        garvis.start()
        
        # Test voice input -> AI response -> voice output
        audio_input = load_test_audio("question.wav")
        
        # Process through entire pipeline
        transcription = garvis.voice_processor.transcribe(audio_input)
        ai_response = garvis.chat(transcription["text"])
        audio_output = garvis.voice_processor.synthesize(ai_response)
        
        assert transcription["text"]
        assert ai_response
        assert len(audio_output) > 0
        
        garvis.stop()
```

### Code Quality

#### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.9
        
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings]
        
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
        additional_dependencies: [types-PyYAML, types-requests]
```

#### Code Style Guidelines

```python
# Example of properly formatted code
class ModelManager:
    """
    Manages AI model lifecycle and operations.
    
    This class handles loading, unloading, and inference operations
    for various AI models in the GarvisNeuralMind system.
    
    Args:
        config: Configuration dictionary containing model settings
        
    Attributes:
        loaded_models: Dictionary of currently loaded models
        default_model: Default model identifier
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.loaded_models: Dict[str, Any] = {}
        self.default_model = config.get("default_model")
        
    def load_model(
        self, 
        model_id: str, 
        backend: str = "auto",
        **kwargs: Any
    ) -> bool:
        """
        Load a model with specified backend.
        
        Args:
            model_id: Unique identifier for the model
            backend: Backend to use for loading (auto, ollama, vllm, etc.)
            **kwargs: Additional backend-specific arguments
            
        Returns:
            True if model loaded successfully, False otherwise
            
        Raises:
            ModelLoadError: If model fails to load
        """
        try:
            # Implementation here
            return True
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            return False
```

---

## Testing Framework

### Test Categories

#### Unit Tests
```python
# tests/unit/models/test_model_manager.py
import pytest
from unittest.mock import Mock, patch
from garvis.models import ModelManager

class TestModelManager:
    @pytest.fixture
    def config(self):
        return {
            "default_model": "test-model",
            "backends": {
                "ollama": {"host": "localhost", "port": 11434}
            }
        }
        
    @pytest.fixture
    def model_manager(self, config):
        return ModelManager(config)
        
    def test_initialization(self, model_manager, config):
        assert model_manager.config == config
        assert model_manager.default_model == "test-model"
        
    @patch('garvis.models.backends.OllamaBackend')
    def test_load_model_ollama(self, mock_ollama, model_manager):
        mock_backend = Mock()
        mock_ollama.return_value = mock_backend
        
        result = model_manager.load_model("test-model", backend="ollama")
        
        assert result is True
        assert "test-model" in model_manager.loaded_models
        mock_ollama.assert_called_once()
```

#### Integration Tests
```python
# tests/integration/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from garvis.api.main import create_app
from garvis.core import GarvisCore

@pytest.fixture
def test_client():
    garvis = GarvisCore("config/test_settings.yaml")
    app = create_app(garvis)
    return TestClient(app)

def test_chat_endpoint(test_client):
    response = test_client.post(
        "/api/chat",
        json={
            "message": "Hello, how are you?",
            "context": {"temperature": 0.7}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "session_id" in data
    assert data["response"]

def test_model_status_endpoint(test_client):
    response = test_client.get("/api/models")
    
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert isinstance(data["models"], list)
```

#### Performance Tests
```python
# tests/performance/test_model_inference.py
import pytest
import time
from garvis.models import ModelManager

@pytest.mark.performance
class TestModelPerformance:
    def test_model_inference_latency(self):
        """Test that model inference completes within acceptable time."""
        model_manager = ModelManager(test_config)
        model_manager.load_model("llama-7b")
        
        prompt = "Explain quantum computing in simple terms."
        
        start_time = time.time()
        response = model_manager.generate(prompt)
        end_time = time.time()
        
        latency = end_time - start_time
        
        assert response  # Ensure we got a response
        assert latency < 30.0  # Should complete within 30 seconds
        
    def test_concurrent_requests(self):
        """Test system performance under concurrent load."""
        import concurrent.futures
        
        def make_request():
            response = model_manager.generate("Hello, world!")
            return len(response) > 0
            
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            results = [future.result() for future in futures]
            
        # All requests should succeed
        assert all(results)
```

### Test Configuration

```yaml
# config/test_settings.yaml
core:
  debug: true
  log_level: "DEBUG"
  
models:
  default_model: "mock-model"
  backends:
    mock:
      responses:
        "Hello": "Hello! How can I help you?"
        
memory:
  backends:
    mock:
      storage: {}
      
voice:
  engines:
    stt:
      primary: "mock"
    tts:
      primary: "mock"
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m performance

# Run with coverage
pytest --cov=src/garvis --cov-report=html

# Run tests in parallel
pytest -n auto

# Generate coverage report
coverage run -m pytest
coverage html
```

---

## Deployment Guide

### Production Deployment with Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Set Python path
ENV PYTHONPATH=/app/src

# Create non-root user
RUN useradd --create-home --shell /bin/bash garvis
USER garvis

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
  CMD curl -f http://localhost:8000/api/status || exit 1

# Run application
CMD ["python", "src/main.py"]
```

### Docker Compose Production

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  garvis:
    build: .
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    env_file:
      - .env.prod
    volumes:
      - models_cache:/app/models
      - logs:/app/logs
    depends_on:
      - redis
      - postgres
      - pinecone-proxy
    deploy:
      resources:
        limits:
          memory: 16G
          cpus: '8'
        reservations:
          memory: 8G
          cpus: '4'
          
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    
  postgres:
    image: postgres:15
    restart: unless-stopped
    environment:
      POSTGRES_DB: garvis_prod
      POSTGRES_USER: garvis
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - garvis

volumes:
  models_cache:
  logs:
  redis_data:
  postgres_data:
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: garvis-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: garvis
  template:
    metadata:
      labels:
        app: garvis
    spec:
      containers:
      - name: garvis
        image: garvis:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        env:
        - name: ENVIRONMENT
          value: "production"
        livenessProbe:
          httpGet:
            path: /api/status
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /api/status
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

### CI/CD Pipeline

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
        
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
        
    - name: Run linting
      run: |
        flake8 src/
        black --check src/
        isort --check-only src/
        
    - name: Run tests
      run: |
        pytest tests/ --cov=src/ --cov-report=xml
        
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        
  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t garvis:${{ github.sha }} .
        docker tag garvis:${{ github.sha }} garvis:latest
        
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push garvis:${{ github.sha }}
        docker push garvis:latest
        
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to production
      run: |
        # Deployment script here
        echo "Deploying to production..."
```

---

## Performance Optimization

### Model Optimization

```python
# Quantization for memory efficiency
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def load_quantized_model(model_name: str):
    """Load model with 8-bit quantization."""
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        load_in_8bit=True,
        device_map="auto",
        torch_dtype=torch.float16
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model, tokenizer

# Model caching strategy
class ModelCache:
    def __init__(self, max_models: int = 3):
        self.cache = {}
        self.max_models = max_models
        self.access_times = {}
        
    def get_model(self, model_id: str):
        if model_id in self.cache:
            self.access_times[model_id] = time.time()
            return self.cache[model_id]
        
        # Load model and manage cache
        if len(self.cache) >= self.max_models:
            self._evict_least_recently_used()
            
        model = self._load_model(model_id)
        self.cache[model_id] = model
        self.access_times[model_id] = time.time()
        return model
```

### Database Optimization

```python
# Connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Async database operations
import asyncpg
import asyncio

class AsyncDatabaseManager:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool = None
        
    async def initialize(self):
        self.pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=5,
            max_size=20
        )
        
    async def execute_query(self, query: str, *args):
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)
```

### Caching Strategies

```python
# Redis caching with TTL
import redis.asyncio as redis
import json

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        
    async def get_cached_response(self, key: str) -> Optional[str]:
        cached = await self.redis.get(key)
        return json.loads(cached) if cached else None
        
    async def cache_response(self, key: str, response: str, ttl: int = 3600):
        await self.redis.setex(key, ttl, json.dumps(response))
        
    async def invalidate_cache(self, pattern: str):
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
```

---

## Troubleshooting

### Common Issues

#### Model Loading Issues
```python
# Debug model loading
def debug_model_loading(model_id: str):
    """Debug model loading issues."""
    try:
        # Check available memory
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory
            gpu_used = torch.cuda.memory_allocated(0)
            print(f"GPU Memory: {gpu_used}/{gpu_memory} bytes")
            
        # Check model path
        model_path = get_model_path(model_id)
        if not os.path.exists(model_path):
            print(f"Model path not found: {model_path}")
            
        # Try loading with different precisions
        for dtype in [torch.float16, torch.float32]:
            try:
                model = load_model(model_id, torch_dtype=dtype)
                print(f"Successfully loaded with {dtype}")
                return model
            except Exception as e:
                print(f"Failed with {dtype}: {e}")
                
    except Exception as e:
        print(f"Model loading failed: {e}")
        return None
```

#### Memory Management
```python
# Memory cleanup utilities
import gc
import torch

def cleanup_gpu_memory():
    """Clean up GPU memory."""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
    gc.collect()

def monitor_memory_usage():
    """Monitor system memory usage."""
    import psutil
    
    # System memory
    memory = psutil.virtual_memory()
    print(f"System Memory: {memory.percent}% used")
    
    # GPU memory
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            gpu_memory = torch.cuda.memory_allocated(i)
            gpu_total = torch.cuda.get_device_properties(i).total_memory
            print(f"GPU {i}: {gpu_memory}/{gpu_total} bytes")
```

### Logging and Monitoring

```python
# Structured logging with context
import structlog

logger = structlog.get_logger(__name__)

def log_request_context(func):
    """Decorator to log request context."""
    def wrapper(*args, **kwargs):
        request_id = generate_request_id()
        
        logger.info(
            "Request started",
            request_id=request_id,
            function=func.__name__,
            args=len(args),
            kwargs=list(kwargs.keys())
        )
        
        try:
            result = func(*args, **kwargs)
            logger.info("Request completed", request_id=request_id)
            return result
        except Exception as e:
            logger.error(
                "Request failed",
                request_id=request_id,
                error=str(e),
                exc_info=True
            )
            raise
            
    return wrapper

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Comprehensive health check."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {}
    }
    
    # Check database
    try:
        await db.execute("SELECT 1")
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        health_status["components"]["database"] = f"unhealthy: {e}"
        health_status["status"] = "unhealthy"
        
    # Check Redis
    try:
        await redis.ping()
        health_status["components"]["redis"] = "healthy"
    except Exception as e:
        health_status["components"]["redis"] = f"unhealthy: {e}"
        health_status["status"] = "unhealthy"
        
    return health_status
```

---

## Contributing Guidelines

### Code Review Process

1. **Pull Request Template**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes without migration path
```

2. **Review Criteria**
- Code quality and style
- Test coverage
- Performance impact
- Security considerations
- Documentation completeness

### Best Practices

1. **Code Organization**
   - Keep functions small and focused
   - Use type hints consistently
   - Follow SOLID principles
   - Implement proper error handling

2. **Testing**
   - Maintain >90% test coverage
   - Write tests before implementation (TDD)
   - Use descriptive test names
   - Mock external dependencies

3. **Documentation**
   - Document all public APIs
   - Include usage examples
   - Keep documentation up to date
   - Use docstrings for all functions/classes

This developer guide provides comprehensive documentation for working with the GarvisNeuralMind system, from initial setup through production deployment and maintenance.