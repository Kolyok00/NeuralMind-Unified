# GarvisNeuralMind API Reference

## Overview

This document provides comprehensive documentation for all public APIs, functions, and components in the GarvisNeuralMind system.

## Table of Contents

1. [REST API Endpoints](#rest-api-endpoints)
2. [WebSocket API](#websocket-api)
3. [Core Components](#core-components)
4. [Model Management](#model-management)
5. [Memory Management](#memory-management)
6. [Integration APIs](#integration-apis)
7. [Configuration](#configuration)
8. [Examples](#examples)

---

## REST API Endpoints

### Chat API

#### `POST /api/chat`
Initiate a conversation with the AI assistant.

**Request Body:**
```json
{
  "message": "string",
  "session_id": "string (optional)",
  "model": "string (optional)",
  "context": {
    "max_tokens": "integer (optional)",
    "temperature": "float (optional)",
    "system_prompt": "string (optional)"
  }
}
```

**Response:**
```json
{
  "response": "string",
  "session_id": "string",
  "model_used": "string",
  "tokens_used": "integer",
  "timestamp": "string (ISO 8601)"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how can you help me?",
    "context": {
      "temperature": 0.7,
      "max_tokens": 500
    }
  }'
```

#### `GET /api/chat/history/{session_id}`
Retrieve chat history for a specific session.

**Response:**
```json
{
  "session_id": "string",
  "messages": [
    {
      "role": "user|assistant",
      "content": "string",
      "timestamp": "string (ISO 8601)"
    }
  ],
  "total_messages": "integer"
}
```

### Memory API

#### `POST /api/memory/store`
Store information in the AI's memory system.

**Request Body:**
```json
{
  "content": "string",
  "metadata": {
    "category": "string",
    "importance": "integer (1-10)",
    "tags": ["string"]
  },
  "embedding_model": "string (optional)"
}
```

**Response:**
```json
{
  "memory_id": "string",
  "status": "stored|failed",
  "embedding_vector": "array (optional)"
}
```

#### `GET /api/memory/search`
Search through stored memories.

**Query Parameters:**
- `query`: Search query string
- `limit`: Maximum number of results (default: 10)
- `threshold`: Similarity threshold (0.0-1.0, default: 0.7)

**Response:**
```json
{
  "results": [
    {
      "memory_id": "string",
      "content": "string",
      "similarity_score": "float",
      "metadata": "object"
    }
  ],
  "total_found": "integer"
}
```

#### `DELETE /api/memory/{memory_id}`
Delete a specific memory.

**Response:**
```json
{
  "status": "deleted|not_found",
  "memory_id": "string"
}
```

### Model Management API

#### `POST /api/fine-tune`
Start a fine-tuning process for a model.

**Request Body:**
```json
{
  "base_model": "string",
  "training_data": "string (file path or data)",
  "config": {
    "learning_rate": "float",
    "epochs": "integer",
    "batch_size": "integer",
    "validation_split": "float"
  },
  "output_model_name": "string"
}
```

**Response:**
```json
{
  "job_id": "string",
  "status": "started|queued|failed",
  "estimated_duration": "string",
  "created_at": "string (ISO 8601)"
}
```

#### `GET /api/fine-tune/{job_id}`
Get status of a fine-tuning job.

**Response:**
```json
{
  "job_id": "string",
  "status": "started|running|completed|failed",
  "progress": "float (0.0-1.0)",
  "current_epoch": "integer",
  "total_epochs": "integer",
  "metrics": {
    "loss": "float",
    "accuracy": "float",
    "validation_loss": "float"
  }
}
```

#### `GET /api/models`
List all available models.

**Response:**
```json
{
  "models": [
    {
      "model_id": "string",
      "name": "string",
      "type": "base|fine-tuned",
      "size": "string",
      "capabilities": ["text", "code", "chat"],
      "status": "available|loading|unavailable"
    }
  ]
}
```

### System Status API

#### `GET /api/status`
Get system status and health information.

**Response:**
```json
{
  "status": "healthy|degraded|unhealthy",
  "uptime": "string",
  "memory_usage": {
    "used": "integer (bytes)",
    "total": "integer (bytes)",
    "percentage": "float"
  },
  "gpu_usage": {
    "utilization": "float (0.0-1.0)",
    "memory_used": "integer (bytes)",
    "temperature": "float (celsius)"
  },
  "active_models": ["string"],
  "database_status": "connected|disconnected"
}
```

---

## WebSocket API

### Connection
Connect to the WebSocket endpoint:
```
ws://localhost:8000/ws/chat
```

### Message Format

#### Client to Server
```json
{
  "type": "message|voice|command",
  "data": {
    "content": "string",
    "session_id": "string (optional)",
    "model": "string (optional)"
  }
}
```

#### Server to Client
```json
{
  "type": "response|error|status",
  "data": {
    "content": "string",
    "session_id": "string",
    "timestamp": "string (ISO 8601)"
  }
}
```

### Real-time Voice Interaction

#### Start Voice Session
```json
{
  "type": "voice_start",
  "data": {
    "sample_rate": 16000,
    "format": "wav|mp3",
    "language": "en|hu"
  }
}
```

#### Send Audio Data
```json
{
  "type": "voice_data",
  "data": {
    "audio": "base64_encoded_audio_chunk"
  }
}
```

#### Voice Response
```json
{
  "type": "voice_response",
  "data": {
    "text": "string",
    "audio": "base64_encoded_audio",
    "duration": "float (seconds)"
  }
}
```

---

## Core Components

### GarvisCore

Main orchestrator class for the AI system.

```python
class GarvisCore:
    def __init__(self, config_path: str = "config/settings.yaml"):
        """
        Initialize the GarvisCore system.
        
        Args:
            config_path: Path to configuration file
        """
        
    def start(self) -> None:
        """Start all system components."""
        
    def stop(self) -> None:
        """Gracefully stop all system components."""
        
    def get_status(self) -> Dict[str, Any]:
        """Get current system status."""
        
    def chat(self, message: str, session_id: str = None) -> str:
        """
        Process a chat message.
        
        Args:
            message: User message
            session_id: Optional session identifier
            
        Returns:
            AI response
        """
```

### ModelManager

Handles AI model loading, switching, and management.

```python
class ModelManager:
    def __init__(self, models_config: Dict[str, Any]):
        """
        Initialize model manager.
        
        Args:
            models_config: Configuration for available models
        """
        
    def load_model(self, model_id: str) -> bool:
        """
        Load a specific model.
        
        Args:
            model_id: Unique model identifier
            
        Returns:
            True if loaded successfully
        """
        
    def unload_model(self, model_id: str) -> bool:
        """Unload a model from memory."""
        
    def list_models(self) -> List[Dict[str, Any]]:
        """Get list of available models."""
        
    def generate(self, prompt: str, model_id: str = None, **kwargs) -> str:
        """
        Generate text using specified model.
        
        Args:
            prompt: Input prompt
            model_id: Model to use (defaults to primary)
            **kwargs: Generation parameters
            
        Returns:
            Generated text
        """
```

### MemoryManager

Manages AI memory storage and retrieval.

```python
class MemoryManager:
    def __init__(self, storage_config: Dict[str, Any]):
        """
        Initialize memory manager.
        
        Args:
            storage_config: Configuration for storage backends
        """
        
    def store(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """
        Store content in memory.
        
        Args:
            content: Content to store
            metadata: Additional metadata
            
        Returns:
            Memory ID
        """
        
    def search(self, query: str, limit: int = 10, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Search stored memories.
        
        Args:
            query: Search query
            limit: Maximum results
            threshold: Similarity threshold
            
        Returns:
            List of matching memories
        """
        
    def retrieve(self, memory_id: str) -> Dict[str, Any]:
        """Retrieve specific memory by ID."""
        
    def delete(self, memory_id: str) -> bool:
        """Delete memory by ID."""
```

### VoiceProcessor

Handles voice input/output processing.

```python
class VoiceProcessor:
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize voice processor.
        
        Args:
            config: Voice processing configuration
        """
        
    def transcribe(self, audio_data: bytes, language: str = "en") -> str:
        """
        Convert speech to text.
        
        Args:
            audio_data: Raw audio data
            language: Language code
            
        Returns:
            Transcribed text
        """
        
    def synthesize(self, text: str, voice: str = "default") -> bytes:
        """
        Convert text to speech.
        
        Args:
            text: Text to synthesize
            voice: Voice model to use
            
        Returns:
            Audio data
        """
        
    def detect_language(self, audio_data: bytes) -> str:
        """Detect language from audio."""
        
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voice models."""
```

---

## Model Management

### Fine-tuning Process

#### FineTuner Class

```python
class FineTuner:
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize fine-tuning system.
        
        Args:
            config: Fine-tuning configuration
        """
        
    def start_job(self, job_config: Dict[str, Any]) -> str:
        """
        Start a fine-tuning job.
        
        Args:
            job_config: Job configuration
            
        Returns:
            Job ID
        """
        
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of fine-tuning job."""
        
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job."""
        
    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all fine-tuning jobs."""
```

#### Usage Example

```python
from garvis.core import GarvisCore
from garvis.models import FineTuner

# Initialize system
garvis = GarvisCore()
fine_tuner = FineTuner(garvis.config.fine_tuning)

# Start fine-tuning
job_config = {
    "base_model": "llama-7b",
    "training_data": "data/custom_dataset.jsonl",
    "config": {
        "learning_rate": 1e-4,
        "epochs": 3,
        "batch_size": 4
    },
    "output_model_name": "custom-llama-7b"
}

job_id = fine_tuner.start_job(job_config)
print(f"Fine-tuning job started: {job_id}")

# Monitor progress
status = fine_tuner.get_job_status(job_id)
print(f"Progress: {status['progress']:.1%}")
```

---

## Memory Management

### Supported Storage Backends

#### Pinecone Integration

```python
class PineconeStorage:
    def __init__(self, api_key: str, environment: str, index_name: str):
        """Initialize Pinecone storage backend."""
        
    def store_embedding(self, vector: List[float], metadata: Dict[str, Any]) -> str:
        """Store vector embedding with metadata."""
        
    def search_similar(self, query_vector: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
```

#### Redis Integration

```python
class RedisStorage:
    def __init__(self, host: str, port: int, db: int = 0):
        """Initialize Redis storage backend."""
        
    def set_cache(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Cache data with TTL."""
        
    def get_cache(self, key: str) -> Any:
        """Retrieve cached data."""
```

#### PostgreSQL Integration

```python
class PostgreSQLStorage:
    def __init__(self, connection_string: str):
        """Initialize PostgreSQL storage backend."""
        
    def store_conversation(self, session_id: str, messages: List[Dict[str, Any]]) -> bool:
        """Store conversation history."""
        
    def get_conversation(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieve conversation history."""
```

---

## Integration APIs

### Browser Control

#### BrowserController Class

```python
class BrowserController:
    def __init__(self, browser_type: str = "chrome"):
        """
        Initialize browser controller.
        
        Args:
            browser_type: Browser to control (chrome, firefox, edge)
        """
        
    def navigate(self, url: str) -> bool:
        """Navigate to URL."""
        
    def click_element(self, selector: str) -> bool:
        """Click element by CSS selector."""
        
    def type_text(self, selector: str, text: str) -> bool:
        """Type text into element."""
        
    def get_page_content(self) -> str:
        """Get current page content."""
        
    def take_screenshot(self) -> bytes:
        """Take screenshot of current page."""
```

### VSCode Integration

#### VSCodeConnector Class

```python
class VSCodeConnector:
    def __init__(self, workspace_path: str):
        """
        Initialize VSCode connector.
        
        Args:
            workspace_path: Path to VSCode workspace
        """
        
    def open_file(self, file_path: str) -> bool:
        """Open file in VSCode."""
        
    def get_current_file(self) -> str:
        """Get currently open file content."""
        
    def insert_code(self, code: str, line: int = None) -> bool:
        """Insert code at specified line."""
        
    def run_command(self, command: str) -> Dict[str, Any]:
        """Execute VSCode command."""
```

### External AI APIs

#### OpenRouter Integration

```python
class OpenRouterConnector:
    def __init__(self, api_key: str):
        """Initialize OpenRouter API connector."""
        
    def chat_completion(self, messages: List[Dict[str, Any]], model: str = "deepseek/deepseek-r1") -> str:
        """Get chat completion from OpenRouter."""
        
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
```

#### Google AI Studio Integration

```python
class GoogleAIConnector:
    def __init__(self, api_key: str):
        """Initialize Google AI Studio connector."""
        
    def generate_content(self, prompt: str, model: str = "gemini-pro") -> str:
        """Generate content using Gemini API."""
        
    def analyze_image(self, image_data: bytes, prompt: str) -> str:
        """Analyze image with multimodal model."""
```

---

## Configuration

### settings.yaml Structure

```yaml
# Core system configuration
core:
  host: "0.0.0.0"
  port: 8000
  debug: false
  log_level: "INFO"

# Model configuration
models:
  default_model: "llama-7b"
  model_cache_size: "8GB"
  gpu_acceleration: true
  available_models:
    - name: "llama-7b"
      type: "text"
      path: "/models/llama-7b"
    - name: "codellama-7b"
      type: "code"
      path: "/models/codellama-7b"

# Memory storage configuration
memory:
  default_backend: "pinecone"
  backends:
    pinecone:
      api_key: "${PINECONE_API_KEY}"
      environment: "us-west1-gcp"
      index_name: "garvis-memory"
    redis:
      host: "localhost"
      port: 6379
      db: 0
    postgresql:
      connection_string: "${DATABASE_URL}"

# Voice processing
voice:
  input:
    sample_rate: 16000
    format: "wav"
    language: "en"
  output:
    voice_model: "default"
    speed: 1.0

# Integration settings
integrations:
  openrouter:
    api_key: "${OPENROUTER_API_KEY}"
    default_model: "deepseek/deepseek-r1"
  google_ai:
    api_key: "${GOOGLE_AI_API_KEY}"
    default_model: "gemini-pro"
  browser:
    default_browser: "chrome"
    headless: false
  vscode:
    workspace_path: "/workspace"
    extensions: ["roo-code", "ui-tars"]

# Fine-tuning settings
fine_tuning:
  output_dir: "/models/fine-tuned"
  max_concurrent_jobs: 2
  default_config:
    learning_rate: 1e-4
    epochs: 3
    batch_size: 4
    validation_split: 0.1
```

### Environment Variables

```bash
# Required API Keys
export PINECONE_API_KEY="your-pinecone-api-key"
export OPENROUTER_API_KEY="your-openrouter-api-key"
export GOOGLE_AI_API_KEY="your-google-ai-api-key"
export DATABASE_URL="postgresql://user:pass@localhost:5432/garvis"

# Optional Settings
export GARVIS_CONFIG_PATH="/path/to/custom/settings.yaml"
export GARVIS_LOG_LEVEL="DEBUG"
export GARVIS_GPU_MEMORY_LIMIT="8GB"
```

---

## Examples

### Basic Chat Example

```python
from garvis.core import GarvisCore

# Initialize system
garvis = GarvisCore()
garvis.start()

# Simple chat
response = garvis.chat("Hello, how are you?")
print(response)

# Chat with session
session_id = "user-123"
response = garvis.chat("What's the weather like?", session_id=session_id)
print(response)

# Clean shutdown
garvis.stop()
```

### Memory Storage Example

```python
from garvis.memory import MemoryManager

# Initialize memory manager
memory = MemoryManager(config['memory'])

# Store information
memory_id = memory.store(
    content="Python is a programming language",
    metadata={
        "category": "programming",
        "importance": 8,
        "tags": ["python", "programming", "language"]
    }
)

# Search memories
results = memory.search("programming language", limit=5)
for result in results:
    print(f"Score: {result['similarity_score']:.2f}")
    print(f"Content: {result['content']}")
```

### Voice Interaction Example

```python
from garvis.voice import VoiceProcessor
import pyaudio

# Initialize voice processor
voice = VoiceProcessor(config['voice'])

# Record audio
def record_audio(duration=5):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True)
    frames = []
    for _ in range(int(16000 / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)
    stream.close()
    p.terminate()
    return b''.join(frames)

# Process voice input
audio_data = record_audio()
text = voice.transcribe(audio_data)
print(f"You said: {text}")

# Generate voice response
response_text = garvis.chat(text)
audio_response = voice.synthesize(response_text)
# Play audio_response...
```

### Fine-tuning Example

```python
from garvis.models import FineTuner
import json

# Prepare training data
training_data = [
    {"input": "What is Python?", "output": "Python is a programming language."},
    {"input": "How do I install packages?", "output": "Use pip install package_name."}
]

with open("training_data.jsonl", "w") as f:
    for item in training_data:
        f.write(json.dumps(item) + "\n")

# Start fine-tuning
fine_tuner = FineTuner(config['fine_tuning'])
job_id = fine_tuner.start_job({
    "base_model": "llama-7b",
    "training_data": "training_data.jsonl",
    "output_model_name": "custom-assistant"
})

# Monitor progress
import time
while True:
    status = fine_tuner.get_job_status(job_id)
    print(f"Status: {status['status']}, Progress: {status.get('progress', 0):.1%}")
    if status['status'] in ['completed', 'failed']:
        break
    time.sleep(30)
```

### Browser Automation Example

```python
from garvis.integrations import BrowserController

# Initialize browser
browser = BrowserController("chrome")

# Navigate and interact
browser.navigate("https://example.com")
browser.click_element("#search-button")
browser.type_text("#search-input", "GarvisNeuralMind")

# Get page content for AI processing
content = browser.get_page_content()
response = garvis.chat(f"Summarize this webpage: {content}")
print(response)
```

---

## Error Handling

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 1001 | Model not found | Check available models with `/api/models` |
| 1002 | GPU memory insufficient | Reduce batch size or unload unused models |
| 1003 | API key invalid | Verify API keys in environment variables |
| 1004 | Storage backend unavailable | Check database/vector store connectivity |
| 1005 | Voice processing failed | Verify audio format and sample rate |

### Error Response Format

```json
{
  "error": {
    "code": 1001,
    "message": "Model 'invalid-model' not found",
    "details": {
      "available_models": ["llama-7b", "codellama-7b"],
      "requested_model": "invalid-model"
    }
  }
}
```

---

## Performance Guidelines

### Optimization Tips

1. **Model Loading**: Keep frequently used models loaded in memory
2. **Memory Management**: Use appropriate storage backends for different data types
3. **Caching**: Enable Redis caching for repeated queries
4. **GPU Usage**: Monitor GPU memory and utilization
5. **Batch Processing**: Process multiple requests together when possible

### Monitoring

```python
# Get system metrics
status = garvis.get_status()
print(f"Memory usage: {status['memory_usage']['percentage']:.1f}%")
print(f"GPU utilization: {status['gpu_usage']['utilization']:.1f}%")
print(f"Active models: {status['active_models']}")
```

---

This API reference provides comprehensive documentation for all public APIs, functions, and components in the GarvisNeuralMind system. For implementation details and advanced configurations, refer to the specific component documentation in the respective modules.