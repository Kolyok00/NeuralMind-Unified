# Installation Guide

This guide will help you install and set up FusionAI Companion on your system.

## Prerequisites

### Required Software

1. **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
   - Download from: <https://www.docker.com/products/docker-desktop/>
   - Make sure Docker Compose is included

2. **Python 3.8+**
   - Download from: <https://www.python.org/downloads/>
   - Make sure to add Python to your system PATH

3. **Git**
   - Download from: <https://git-scm.com/downloads/>

### Recommended Hardware

- **RAM**: 8GB minimum, 16GB+ recommended
- **Storage**: 20GB free space
- **GPU**: Optional but recommended for local AI models (NVIDIA GPU with CUDA support)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Kolyok00/FusionAI-Companion.git
cd FusionAI-Companion
```

### 2. Environment Setup

#### Option A: Automated Setup (Recommended)

**Windows (PowerShell):**

```powershell
.\start.ps1
```

**Windows (Command Prompt):**

```batch
start.bat
```

**Linux/Mac:**

```bash
chmod +x setup.sh
./setup.sh
```

#### Option B: Manual Setup

1. **Create Python Virtual Environment:**

```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

2. **Install Python Dependencies:**

```bash
pip install -r requirements.txt
```

3. **Configure Environment:**

```bash
cp .env.example .env
# Edit .env file with your API keys
```

4. **Start Docker Services:**

```bash
docker-compose up -d
```

5. **Initialize Git Submodules:**

```bash
git submodule init
git submodule update --recursive
```

### 3. Configuration

Edit the `.env` file with your API keys and configuration:

```bash
# LLM Provider API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Database Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
NEO4J_PASSWORD=your_neo4j_password_here

# Security
JWT_SECRET=your-secret-key-here
```

### 4. Download AI Models

The setup script will automatically download essential models. To manually download:

```bash
# Connect to Ollama container
docker exec -it fusionai-ollama ollama pull qwen2:7b
docker exec -it fusionai-ollama ollama pull mistral:7b
docker exec -it fusionai-ollama ollama pull deepseek-coder:6.7b
docker exec -it fusionai-ollama ollama pull nomic-embed-text
```

### 5. Start the Application

```bash
python main.py
```

## Verification

After installation, verify that all services are running:

1. **Web UI**: <http://localhost:8888>
2. **Open WebUI (Chat)**: <http://localhost:3000>
3. **n8n Workflows**: <http://localhost:5678>
4. **Langfuse Monitoring**: <http://localhost:3001>
5. **Neo4j Browser**: <http://localhost:7474>
6. **SearXNG Search**: <http://localhost:8080>

## Troubleshooting

### Common Issues

#### Docker Services Not Starting

1. Check if Docker Desktop is running
2. Ensure no other services are using the required ports
3. Try restarting Docker Desktop

```bash
# Stop all services
docker-compose down

# Restart with logs
docker-compose up -d
docker-compose logs -f
```

#### Python Dependencies Issues

1. Make sure you're using Python 3.8+
2. Update pip: `pip install --upgrade pip`
3. Clear pip cache: `pip cache purge`

#### API Keys Not Working

1. Verify API keys are correct in `.env` file
2. Check API key permissions and quotas
3. Ensure no extra spaces or quotes around keys

#### Ollama Models Not Loading

1. Check if Ollama container is running: `docker ps`
2. Check Ollama logs: `docker logs fusionai-ollama`
3. Manually pull models:

```bash
docker exec -it fusionai-ollama ollama pull qwen2:7b
```

#### Port Conflicts

If you get port conflicts, edit `docker-compose.yml` to use different ports:

```yaml
ports:
  - "11435:11434"  # Change first port number
```

### Getting Help

1. Check the logs: `docker-compose logs -f`
2. Check service health: `python main.py --health-check`
3. Create an issue on GitHub with logs and error messages

## Next Steps

After successful installation:

1. **Configure AI Models**: Add your preferred models in the configuration
2. **Set up Workflows**: Import n8n workflows from the `workflows/` directory
3. **Configure VTuber**: If using VTuber features, set up your VRM model
4. **Explore Documentation**: Read the module-specific documentation
5. **Join Community**: Connect with other users for tips and support

## Updating

To update FusionAI Companion:

```bash
# Pull latest changes
git pull origin main

# Update submodules
git submodule update --recursive

# Update Python dependencies
pip install -r requirements.txt --upgrade

# Update Docker images
docker-compose pull
docker-compose up -d --build
```

## Uninstalling

To completely remove FusionAI Companion:

```bash
# Stop and remove containers
docker-compose down -v

# Remove Docker images
docker rmi $(docker images "fusionai*" -q)

# Remove the project directory
cd ..
rm -rf FusionAI-Companion
```
