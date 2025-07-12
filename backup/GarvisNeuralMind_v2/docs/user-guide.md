# GarvisNeuralMind User Guide

## Overview

This comprehensive user guide provides step-by-step instructions, tutorials, and examples for using the GarvisNeuralMind AI assistant system effectively.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Advanced Features](#advanced-features)
4. [Voice Integration](#voice-integration)
5. [Memory Management](#memory-management)
6. [Browser Automation](#browser-automation)
7. [VSCode Integration](#vscode-integration)
8. [API Usage Examples](#api-usage-examples)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

---

## Getting Started

### System Requirements

- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Memory**: 8GB RAM minimum, 16GB recommended
- **Storage**: 50GB free space (for models and data)
- **Internet**: Stable internet connection for API services
- **Hardware**: GPU optional but recommended for better performance

### Installation

#### Quick Start with Docker

```bash
# Download and run GarvisNeuralMind
docker run -d \
  --name garvis \
  -p 8000:8000 \
  -e OPENROUTER_API_KEY=your_openrouter_key \
  -e GOOGLE_AI_API_KEY=your_google_ai_key \
  garvis/neuralmind:latest

# Check if running
curl http://localhost:8000/api/status
```

#### Manual Installation

```bash
# Clone repository
git clone https://github.com/your-org/GarvisNeuralMind.git
cd GarvisNeuralMind

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start the system
python src/main.py
```

### Initial Configuration

Create your configuration file:

```yaml
# config/user_settings.yaml
core:
  host: "0.0.0.0"
  port: 8000
  
models:
  default_model: "llama-7b"
  
integrations:
  openrouter:
    api_key: "your-openrouter-api-key"
  google_ai:
    api_key: "your-google-ai-api-key"
    
voice:
  input:
    language: "en"  # or "hu" for Hungarian
  output:
    voice_model: "default"
```

---

## Basic Usage

### Text Chat Interface

#### Using the Web Interface

1. Open your browser and navigate to `http://localhost:8000`
2. You'll see the GarvisNeuralMind chat interface
3. Type your message in the input field
4. Press Enter or click Send

#### Example Conversations

**Basic Q&A:**
```
User: Hello! How are you today?
Garvis: Hello! I'm doing well, thank you for asking. I'm here and ready to help you with any questions or tasks you might have. How can I assist you today?

User: Can you explain quantum computing in simple terms?
Garvis: Quantum computing is like having a super-powered calculator that works very differently from regular computers. Instead of using bits that are either 0 or 1, quantum computers use "qubits" that can be both 0 and 1 at the same time. This allows them to process many possibilities simultaneously, making them potentially much faster at solving certain complex problems like breaking codes or simulating molecules.
```

**Technical Support:**
```
User: I'm having trouble with my Python code. Can you help debug this?
Garvis: I'd be happy to help debug your Python code! Please share the code you're having trouble with, along with any error messages you're seeing, and I'll help you identify and fix the issues.

User: Here's my code: [code snippet]
Garvis: I can see the issue in your code. On line 5, you have a syntax error...
```

### API Usage

#### Using cURL

```bash
# Basic chat request
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is machine learning?",
    "context": {
      "temperature": 0.7,
      "max_tokens": 500
    }
  }'

# Response
{
  "response": "Machine learning is a subset of artificial intelligence...",
  "session_id": "session_123",
  "model_used": "llama-7b",
  "tokens_used": 156,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Using Python

```python
import requests

# Initialize client
class GarvisClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session_id = None
        
    def chat(self, message, **kwargs):
        payload = {
            "message": message,
            "session_id": self.session_id,
            "context": kwargs
        }
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            self.session_id = data["session_id"]
            return data["response"]
        else:
            raise Exception(f"Error: {response.status_code}")

# Usage example
client = GarvisClient()

# Start conversation
response = client.chat("Hello, introduce yourself.")
print(response)

# Continue conversation (session maintained)
response = client.chat("What can you help me with?")
print(response)

# Use custom parameters
response = client.chat(
    "Write a creative story",
    temperature=0.9,
    max_tokens=300
)
print(response)
```

---

## Advanced Features

### Custom Model Fine-tuning

#### Preparing Training Data

```python
# Create training dataset
import json

training_data = [
    {
        "input": "What is the best programming language for AI?",
        "output": "Python is widely considered the best programming language for AI due to its extensive libraries like TensorFlow, PyTorch, and scikit-learn, along with its simple syntax and large community support."
    },
    {
        "input": "How do I optimize neural networks?",
        "output": "Neural network optimization involves several techniques: proper data preprocessing, choosing appropriate architectures, using regularization methods like dropout, optimizing hyperparameters, and implementing early stopping to prevent overfitting."
    }
]

# Save as JSONL format
with open("custom_training_data.jsonl", "w") as f:
    for item in training_data:
        f.write(json.dumps(item) + "\n")
```

#### Starting Fine-tuning

```python
import requests

# Start fine-tuning job
fine_tune_config = {
    "base_model": "llama-7b",
    "training_data": "custom_training_data.jsonl",
    "config": {
        "learning_rate": 1e-4,
        "epochs": 3,
        "batch_size": 4,
        "validation_split": 0.1
    },
    "output_model_name": "custom-assistant-v1"
}

response = requests.post(
    "http://localhost:8000/api/fine-tune",
    json=fine_tune_config
)

job_id = response.json()["job_id"]
print(f"Fine-tuning job started: {job_id}")

# Monitor progress
import time

while True:
    status_response = requests.get(f"http://localhost:8000/api/fine-tune/{job_id}")
    status = status_response.json()
    
    print(f"Status: {status['status']}, Progress: {status.get('progress', 0):.1%}")
    
    if status['status'] in ['completed', 'failed']:
        break
        
    time.sleep(30)  # Check every 30 seconds
```

### Memory and Context Management

#### Storing Important Information

```python
# Store user preferences
memory_data = {
    "content": "User prefers detailed technical explanations with code examples",
    "metadata": {
        "category": "user_preference",
        "user_id": "john_doe",
        "importance": 8,
        "tags": ["communication_style", "technical", "coding"]
    }
}

response = requests.post(
    "http://localhost:8000/api/memory/store",
    json=memory_data
)

memory_id = response.json()["memory_id"]
print(f"Stored memory with ID: {memory_id}")
```

#### Searching Memories

```python
# Search for relevant memories
search_params = {
    "query": "user communication preferences",
    "limit": 5,
    "threshold": 0.7
}

response = requests.get(
    "http://localhost:8000/api/memory/search",
    params=search_params
)

memories = response.json()["results"]
for memory in memories:
    print(f"Score: {memory['similarity_score']:.2f}")
    print(f"Content: {memory['content']}")
    print("---")
```

---

## Voice Integration

### Basic Voice Setup

#### Web Browser Voice Interface

```html
<!DOCTYPE html>
<html>
<head>
    <title>Garvis Voice Interface</title>
</head>
<body>
    <button id="startRecord">Start Recording</button>
    <button id="stopRecord">Stop Recording</button>
    <div id="transcript"></div>
    <audio id="audioPlayer" controls></audio>

    <script>
        let mediaRecorder;
        let audioChunks = [];
        let websocket;

        // Initialize WebSocket connection
        websocket = new WebSocket('ws://localhost:8000/ws/chat');

        document.getElementById('startRecord').onclick = async () => {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const reader = new FileReader();
                
                reader.onload = () => {
                    const base64Audio = reader.result.split(',')[1];
                    
                    // Send audio to Garvis
                    websocket.send(JSON.stringify({
                        type: 'voice_data',
                        data: { audio: base64Audio }
                    }));
                };
                
                reader.readAsDataURL(audioBlob);
                audioChunks = [];
            };
            
            mediaRecorder.start();
        };

        document.getElementById('stopRecord').onclick = () => {
            mediaRecorder.stop();
        };

        // Handle responses from Garvis
        websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'voice_response') {
                // Display transcript
                document.getElementById('transcript').textContent = data.data.text;
                
                // Play audio response
                const audioBlob = new Blob([
                    Uint8Array.from(atob(data.data.audio), c => c.charCodeAt(0))
                ], { type: 'audio/mpeg' });
                
                const audioUrl = URL.createObjectURL(audioBlob);
                document.getElementById('audioPlayer').src = audioUrl;
                document.getElementById('audioPlayer').play();
            }
        };
    </script>
</body>
</html>
```

#### Python Voice Client

```python
import pyaudio
import websocket
import json
import base64
import threading
import time

class VoiceClient:
    def __init__(self, ws_url="ws://localhost:8000/ws/chat"):
        self.ws_url = ws_url
        self.ws = None
        self.is_recording = False
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk = 1024
        
    def connect(self):
        """Connect to WebSocket."""
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        
        # Start WebSocket in separate thread
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()
        
        time.sleep(1)  # Wait for connection
        
    def start_voice_session(self):
        """Start voice recording session."""
        # Initialize voice session
        self.ws.send(json.dumps({
            "type": "voice_start",
            "data": {
                "sample_rate": self.rate,
                "format": "wav",
                "language": "en"
            }
        }))
        
        # Start recording
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        print("Recording... Press Ctrl+C to stop")
        self.is_recording = True
        
        try:
            while self.is_recording:
                data = stream.read(self.chunk)
                
                # Send audio chunk
                self.ws.send(json.dumps({
                    "type": "voice_data",
                    "data": {
                        "audio": base64.b64encode(data).decode()
                    }
                }))
                
        except KeyboardInterrupt:
            print("\nStopping recording...")
            
        finally:
            self.is_recording = False
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # End voice session
            self.ws.send(json.dumps({"type": "voice_end"}))
            
    def on_message(self, ws, message):
        """Handle WebSocket messages."""
        data = json.loads(message)
        
        if data["type"] == "voice_response":
            print(f"Garvis: {data['data']['text']}")
            
            # Optionally play audio response
            # self.play_audio(data['data']['audio'])
            
    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")
        
    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")

# Usage
if __name__ == "__main__":
    client = VoiceClient()
    client.connect()
    client.start_voice_session()
```

---

## Memory Management

### Personal Assistant Memory

```python
class PersonalAssistant:
    def __init__(self, garvis_client):
        self.client = garvis_client
        self.user_profile = self.load_user_profile()
        
    def load_user_profile(self):
        """Load user profile from memory."""
        response = requests.get(
            "http://localhost:8000/api/memory/search",
            params={
                "query": "user profile preferences",
                "limit": 10
            }
        )
        
        profile = {}
        for memory in response.json()["results"]:
            if memory["metadata"].get("category") == "user_profile":
                profile.update(memory["metadata"])
                
        return profile
        
    def remember_preference(self, preference_type, value):
        """Store user preference."""
        memory_data = {
            "content": f"User prefers {preference_type}: {value}",
            "metadata": {
                "category": "user_profile",
                "preference_type": preference_type,
                "value": value,
                "timestamp": time.time()
            }
        }
        
        response = requests.post(
            "http://localhost:8000/api/memory/store",
            json=memory_data
        )
        
        return response.json()["memory_id"]
        
    def contextual_chat(self, message):
        """Chat with context from memory."""
        # Search for relevant context
        context_response = requests.get(
            "http://localhost:8000/api/memory/search",
            params={
                "query": message,
                "limit": 3
            }
        )
        
        context = []
        for memory in context_response.json()["results"]:
            context.append(memory["content"])
            
        # Include context in chat
        enhanced_message = f"Context: {'; '.join(context)}\n\nUser: {message}"
        
        return self.client.chat(enhanced_message)

# Usage example
assistant = PersonalAssistant(GarvisClient())

# Remember user preferences
assistant.remember_preference("communication_style", "detailed technical explanations")
assistant.remember_preference("programming_language", "Python")

# Chat with context
response = assistant.contextual_chat("How do I optimize my code?")
print(response)
```

---

## Browser Automation

### Web Scraping and Automation

```python
import asyncio
from playwright.async_api import async_playwright

class WebAutomationClient:
    def __init__(self, garvis_url="http://localhost:8000"):
        self.garvis_url = garvis_url
        
    async def automate_web_task(self, instruction, url):
        """Automate web task using natural language instruction."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            # Navigate to URL
            await page.goto(url)
            
            # Take screenshot for AI analysis
            screenshot = await page.screenshot()
            
            # Get page structure
            page_content = await page.content()
            
            # Send to Garvis for analysis and action plan
            automation_request = {
                "instruction": instruction,
                "url": url,
                "page_content": page_content[:5000],  # Limit content size
                "screenshot": base64.b64encode(screenshot).decode()
            }
            
            response = requests.post(
                f"{self.garvis_url}/api/browser/analyze",
                json=automation_request
            )
            
            action_plan = response.json()["action_plan"]
            
            # Execute action plan
            for action in action_plan:
                if action["type"] == "click":
                    await page.click(action["selector"])
                elif action["type"] == "type":
                    await page.fill(action["selector"], action["text"])
                elif action["type"] == "wait":
                    await page.wait_for_timeout(action["duration"])
                    
            # Return results
            final_content = await page.content()
            final_screenshot = await page.screenshot()
            
            await browser.close()
            
            return {
                "success": True,
                "final_content": final_content,
                "final_screenshot": base64.b64encode(final_screenshot).decode()
            }

# Usage examples
async def main():
    automator = WebAutomationClient()
    
    # Example 1: Search for information
    result = await automator.automate_web_task(
        "Search for 'machine learning tutorials' on Google and get the first 3 results",
        "https://google.com"
    )
    
    # Example 2: Form filling
    result = await automator.automate_web_task(
        "Fill out the contact form with name 'John Doe' and email 'john@example.com'",
        "https://example.com/contact"
    )
    
    # Example 3: Data extraction
    result = await automator.automate_web_task(
        "Extract all product names and prices from this e-commerce page",
        "https://shop.example.com"
    )

# Run automation
asyncio.run(main())
```

### Research Assistant

```python
class ResearchAssistant:
    def __init__(self, garvis_client, web_automator):
        self.garvis = garvis_client
        self.web_automator = web_automator
        
    async def research_topic(self, topic, sources=None):
        """Research a topic using multiple sources."""
        if sources is None:
            sources = [
                "https://wikipedia.org",
                "https://scholar.google.com",
                "https://arxiv.org"
            ]
            
        research_results = []
        
        for source in sources:
            try:
                # Use AI to generate search strategy
                search_instruction = f"Research '{topic}' on this website and summarize key findings"
                
                result = await self.web_automator.automate_web_task(
                    search_instruction, source
                )
                
                # Extract and summarize content
                summary_response = self.garvis.chat(
                    f"Summarize the key points about '{topic}' from this content: {result['final_content'][:2000]}"
                )
                
                research_results.append({
                    "source": source,
                    "summary": summary_response,
                    "screenshot": result["final_screenshot"]
                })
                
            except Exception as e:
                print(f"Error researching {source}: {e}")
                
        # Generate comprehensive report
        all_summaries = "\n\n".join([r["summary"] for r in research_results])
        
        final_report = self.garvis.chat(
            f"Create a comprehensive research report about '{topic}' based on these summaries:\n\n{all_summaries}"
        )
        
        return {
            "topic": topic,
            "report": final_report,
            "sources": research_results
        }

# Usage
async def research_example():
    garvis_client = GarvisClient()
    web_automator = WebAutomationClient()
    researcher = ResearchAssistant(garvis_client, web_automator)
    
    report = await researcher.research_topic("quantum computing applications")
    
    print("Research Report:")
    print("=" * 50)
    print(report["report"])
    
    # Save report
    with open(f"research_report_{report['topic'].replace(' ', '_')}.md", "w") as f:
        f.write(f"# Research Report: {report['topic']}\n\n")
        f.write(report["report"])
        f.write("\n\n## Sources\n")
        for source in report["sources"]:
            f.write(f"- {source['source']}\n")

asyncio.run(research_example())
```

---

## VSCode Integration

### Code Analysis and Generation

```python
import os
import subprocess
import json

class VSCodeIntegration:
    def __init__(self, garvis_client, workspace_path):
        self.garvis = garvis_client
        self.workspace_path = workspace_path
        
    def analyze_codebase(self):
        """Analyze entire codebase structure."""
        analysis = {
            "files": [],
            "languages": {},
            "complexity": 0,
            "issues": []
        }
        
        for root, dirs, files in os.walk(self.workspace_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
            
            for file in files:
                if not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.workspace_path)
                    
                    # Detect language
                    ext = os.path.splitext(file)[1]
                    language = self.detect_language(ext)
                    
                    if language:
                        analysis["files"].append({
                            "path": relative_path,
                            "language": language,
                            "size": os.path.getsize(file_path)
                        })
                        
                        analysis["languages"][language] = analysis["languages"].get(language, 0) + 1
                        
        return analysis
        
    def detect_language(self, extension):
        """Detect programming language from file extension."""
        lang_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby'
        }
        return lang_map.get(extension.lower())
        
    def get_code_suggestions(self, file_path):
        """Get AI-powered code suggestions."""
        try:
            with open(os.path.join(self.workspace_path, file_path), 'r') as f:
                code_content = f.read()
                
            # Ask Garvis for code review
            suggestion_prompt = f"""
            Please review this code and provide suggestions for improvement:
            
            File: {file_path}
            Code:
            ```
            {code_content}
            ```
            
            Focus on:
            1. Code quality and readability
            2. Performance optimizations
            3. Best practices
            4. Potential bugs
            5. Security concerns
            """
            
            suggestions = self.garvis.chat(suggestion_prompt)
            return suggestions
            
        except Exception as e:
            return f"Error analyzing file: {e}"
            
    def generate_documentation(self, file_path):
        """Generate documentation for code file."""
        try:
            with open(os.path.join(self.workspace_path, file_path), 'r') as f:
                code_content = f.read()
                
            doc_prompt = f"""
            Generate comprehensive documentation for this code:
            
            File: {file_path}
            Code:
            ```
            {code_content}
            ```
            
            Include:
            1. Overview of functionality
            2. Function/class descriptions
            3. Parameters and return values
            4. Usage examples
            5. Dependencies
            """
            
            documentation = self.garvis.chat(doc_prompt)
            
            # Save documentation
            doc_file = os.path.splitext(file_path)[0] + "_documentation.md"
            with open(os.path.join(self.workspace_path, doc_file), 'w') as f:
                f.write(documentation)
                
            return doc_file
            
        except Exception as e:
            return f"Error generating documentation: {e}"
            
    def generate_tests(self, file_path):
        """Generate unit tests for code file."""
        try:
            with open(os.path.join(self.workspace_path, file_path), 'r') as f:
                code_content = f.read()
                
            test_prompt = f"""
            Generate comprehensive unit tests for this code:
            
            File: {file_path}
            Code:
            ```
            {code_content}
            ```
            
            Generate tests that:
            1. Cover all functions/methods
            2. Test edge cases
            3. Include proper assertions
            4. Follow testing best practices
            5. Use appropriate testing framework
            """
            
            test_code = self.garvis.chat(test_prompt)
            
            # Save test file
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            test_file = f"test_{base_name}.py"
            test_path = os.path.join(self.workspace_path, "tests", test_file)
            
            os.makedirs(os.path.dirname(test_path), exist_ok=True)
            with open(test_path, 'w') as f:
                f.write(test_code)
                
            return test_path
            
        except Exception as e:
            return f"Error generating tests: {e}"

# Usage examples
def main():
    garvis_client = GarvisClient()
    vscode_integration = VSCodeIntegration(garvis_client, "/path/to/your/project")
    
    # Analyze codebase
    analysis = vscode_integration.analyze_codebase()
    print("Codebase Analysis:")
    print(json.dumps(analysis, indent=2))
    
    # Get suggestions for specific file
    suggestions = vscode_integration.get_code_suggestions("src/main.py")
    print("\nCode Suggestions:")
    print(suggestions)
    
    # Generate documentation
    doc_file = vscode_integration.generate_documentation("src/utils.py")
    print(f"\nDocumentation generated: {doc_file}")
    
    # Generate tests
    test_file = vscode_integration.generate_tests("src/calculator.py")
    print(f"Tests generated: {test_file}")

if __name__ == "__main__":
    main()
```

---

## API Usage Examples

### Advanced API Patterns

#### Streaming Responses

```python
import requests
import json

def stream_chat_response(message, session_id=None):
    """Stream chat response for real-time display."""
    payload = {
        "message": message,
        "session_id": session_id,
        "stream": True
    }
    
    response = requests.post(
        "http://localhost:8000/api/chat/stream",
        json=payload,
        stream=True
    )
    
    full_response = ""
    
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode('utf-8'))
            
            if data.get("type") == "token":
                token = data["data"]["token"]
                full_response += token
                print(token, end="", flush=True)
            elif data.get("type") == "complete":
                print("\n")
                return {
                    "response": full_response,
                    "session_id": data["data"]["session_id"]
                }

# Usage
result = stream_chat_response("Tell me a story about a robot")
```

#### Batch Processing

```python
def batch_process_messages(messages):
    """Process multiple messages in batch."""
    batch_payload = {
        "messages": [
            {"id": i, "message": msg} for i, msg in enumerate(messages)
        ],
        "config": {
            "temperature": 0.7,
            "max_tokens": 200
        }
    }
    
    response = requests.post(
        "http://localhost:8000/api/chat/batch",
        json=batch_payload
    )
    
    return response.json()["responses"]

# Usage
messages = [
    "What is Python?",
    "Explain machine learning",
    "How do neural networks work?"
]

responses = batch_process_messages(messages)
for i, response in enumerate(responses):
    print(f"Q{i+1}: {messages[i]}")
    print(f"A{i+1}: {response['response']}")
    print("---")
```

---

## Troubleshooting

### Common Issues and Solutions

#### Connection Issues

```python
def diagnose_connection():
    """Diagnose connection issues with Garvis."""
    print("Diagnosing Garvis connection...")
    
    # Test basic connectivity
    try:
        response = requests.get("http://localhost:8000/api/status", timeout=5)
        if response.status_code == 200:
            print("✓ Garvis is running and accessible")
            status = response.json()
            print(f"  Status: {status.get('status', 'unknown')}")
            print(f"  Uptime: {status.get('uptime', 'unknown')}")
        else:
            print(f"✗ Garvis returned status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Garvis. Is it running?")
        print("  Try: docker ps | grep garvis")
    except requests.exceptions.Timeout:
        print("✗ Connection timeout. Garvis may be overloaded.")
    
    # Test model availability
    try:
        response = requests.get("http://localhost:8000/api/models", timeout=10)
        if response.status_code == 200:
            models = response.json()["models"]
            print(f"✓ {len(models)} models available")
            for model in models:
                print(f"  - {model['name']}: {model['status']}")
        else:
            print("✗ Cannot fetch model status")
    except Exception as e:
        print(f"✗ Error checking models: {e}")

# Run diagnosis
diagnose_connection()
```

#### Performance Issues

```python
import time

def benchmark_performance():
    """Benchmark Garvis performance."""
    print("Running performance benchmark...")
    
    test_messages = [
        "Hello, how are you?",
        "Explain quantum computing",
        "Write a Python function to sort a list",
        "What is the capital of France?",
        "Tell me a joke"
    ]
    
    results = []
    
    for i, message in enumerate(test_messages):
        print(f"Test {i+1}/5: {message[:30]}...")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                "http://localhost:8000/api/chat",
                json={"message": message},
                timeout=30
            )
            
            end_time = time.time()
            latency = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                results.append({
                    "message": message,
                    "latency": latency,
                    "tokens": data.get("tokens_used", 0),
                    "success": True
                })
                print(f"  ✓ {latency:.2f}s, {data.get('tokens_used', 0)} tokens")
            else:
                results.append({
                    "message": message,
                    "latency": latency,
                    "success": False,
                    "error": response.status_code
                })
                print(f"  ✗ Failed: {response.status_code}")
                
        except Exception as e:
            end_time = time.time()
            results.append({
                "message": message,
                "latency": end_time - start_time,
                "success": False,
                "error": str(e)
            })
            print(f"  ✗ Error: {e}")
    
    # Summary
    successful = [r for r in results if r["success"]]
    if successful:
        avg_latency = sum(r["latency"] for r in successful) / len(successful)
        print(f"\nSummary:")
        print(f"  Success rate: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.1f}%)")
        print(f"  Average latency: {avg_latency:.2f}s")
        print(f"  Min latency: {min(r['latency'] for r in successful):.2f}s")
        print(f"  Max latency: {max(r['latency'] for r in successful):.2f}s")
    else:
        print("No successful requests!")

# Run benchmark
benchmark_performance()
```

---

## FAQ

### General Questions

**Q: What models does GarvisNeuralMind support?**
A: GarvisNeuralMind supports various models including Llama, CodeLlama, GPT-4, Gemini, and custom fine-tuned models. You can see available models using the `/api/models` endpoint.

**Q: Can I use GarvisNeuralMind offline?**
A: Yes, for local models like Ollama or vLLM. However, some features like OpenRouter or Google AI integration require internet connectivity.

**Q: How much memory does GarvisNeuralMind require?**
A: This depends on the models you're running. Small models need 4-8GB RAM, while large models may require 16-32GB RAM and GPU memory.

### Technical Questions

**Q: How do I add my own model?**
A: You can add custom models by:
1. Placing model files in the models directory
2. Updating the configuration in `settings.yaml`
3. Restarting GarvisNeuralMind

**Q: Can I integrate with other AI services?**
A: Yes, GarvisNeuralMind supports integration with various AI services through its plugin architecture. See the Integration Guide for details.

**Q: How do I backup my data?**
A: Backup the following directories:
- `config/` - Configuration files
- `models/` - Local model files
- Database files (if using local storage)
- Memory storage (vector databases)

This comprehensive user guide provides everything you need to effectively use GarvisNeuralMind for various AI-powered tasks and workflows.