# VTuber - Avatar and Streaming Components

This directory contains the VTuber avatar and streaming components using SnekStudio and related technologies.

## Setup Instructions

1. Add the SnekStudio submodule:
```bash
git submodule add https://github.com/ExpiredPopsicle/SnekStudio vtuber
```

2. Ensure you have the required dependencies for audio processing
3. Configure OBS Studio for streaming integration

## Components

### SnekStudio VTuber System
- VRM model support
- Real-time avatar animation
- Facial expression mapping
- Lip sync with audio
- Motion capture integration

### Audio Processing
- **Whisper.cpp**: Speech-to-text conversion
- **Chatterbox TTS**: Text-to-speech synthesis
- **Audio Pipeline**: Real-time audio processing
- **Voice Activity Detection**: Smart microphone handling

### Streaming Integration
- **OBS Studio**: Streaming software integration
- **WebSocket API**: Real-time communication
- **Overlay System**: Chat and interaction overlays
- **Scene Management**: Automated scene switching

## VRM Model Setup

### Model Requirements
- Compatible VRM 0.x or 1.0 models
- Recommended polygon count: 10k-50k triangles
- Proper bone hierarchy for animation
- Facial blend shapes for expressions

### Model Configuration
1. Place VRM files in `models/` directory
2. Configure model path in `.env` file:
   ```
   SNEKSTUDIO_MODEL_PATH=./vtuber/models/your-model.vrm
   ```
3. Test model loading and animation

## Audio Configuration

### Speech-to-Text (Whisper)
- Model selection: base, small, medium, large
- Language detection and transcription
- Real-time processing optimization
- Custom vocabulary support

### Text-to-Speech (Chatterbox)
- Multiple voice options
- Speed and pitch control
- Emotion and tone adjustment
- Hungarian language support

### Audio Pipeline
```
Microphone → Whisper STT → AI Processing → TTS → Avatar Animation
```

## Streaming Setup

### OBS Studio Integration
1. Install OBS WebSocket plugin
2. Configure connection in `.env`:
   ```
   OBS_WEBSOCKET_URL=ws://localhost:4455
   OBS_WEBSOCKET_PASSWORD=your_password
   ```
3. Set up scenes for different streaming modes

### Chat Integration
- Real-time chat display
- AI-powered chat responses
- Moderation and filtering
- Custom chat commands

## Usage Examples

### Basic VTuber Session
```bash
# Start the VTuber system
docker-compose up vtuber-stack

# Access the control interface
open http://localhost:8090
```

### AI Chat Integration
```python
# Connect chat to AI system
import websocket

def on_chat_message(message):
    # Process with AI
    ai_response = process_with_ai(message)

    # Convert to speech
    tts_audio = generate_speech(ai_response)

    # Animate avatar
    animate_avatar(tts_audio)
```

### Custom Animations
```python
# Trigger custom avatar animations
def trigger_emotion(emotion_type):
    websocket.send({
        "type": "animation",
        "emotion": emotion_type,
        "intensity": 0.8
    })
```

## Configuration Files

### Avatar Settings
- `config/avatar.json`: Avatar appearance and behavior
- `config/animations.json`: Custom animation definitions
- `config/expressions.json`: Facial expression mappings

### Audio Settings
- `config/audio.json`: Audio processing parameters
- `config/voices.json`: TTS voice configurations
- `config/whisper.json`: STT model settings

## Streaming Scenarios

### Interactive AI Companion
- Real-time conversation with viewers
- Context-aware responses
- Personality and character consistency
- Multi-language support

### Educational Content
- AI-powered tutoring
- Code explanation and demonstration
- Interactive Q&A sessions
- Live problem-solving

### Entertainment Streaming
- AI-generated stories and content
- Interactive games and challenges
- Music and singing (with proper licensing)
- Collaborative creative projects

## Performance Optimization

### Hardware Requirements
- GPU: GTX 1060 / RTX 3060 or better
- RAM: 16GB minimum, 32GB recommended
- CPU: 8+ cores for simultaneous AI processing
- Storage: SSD for model loading

### Optimization Tips
- Use smaller AI models for real-time response
- Implement audio buffering for smoother playback
- Optimize VRM model polygon count
- Use hardware acceleration when available

## Integration Points

- **Open WebUI**: Chat interface
- **Ollama**: Local AI inference
- **Whisper.cpp**: Speech recognition
- **n8n**: Workflow automation
- **Langfuse**: Performance monitoring
- **OBS Studio**: Streaming platform
