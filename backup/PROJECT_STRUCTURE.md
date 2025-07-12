# NeuralMind Project Structure

## Overview

NeuralMind egy komplex AI ökoszisztéma, amely több különböző AI rendszert integrál egy egységes platformon.

## Directory Structure

```
NeuralMind/
├── .vscode/                    # VS Code workspace settings
├── GarvisNeuralMind_v2/        # GarvisNeuralMind AI rendszer
│   ├── config/                 # Konfigurációs fájlok
│   ├── src/                    # Forráskód
│   ├── docs/                   # Dokumentáció
│   ├── tests/                  # Tesztek
│   └── requirements.txt        # Python függőségek
├── FusionAI-Companion0/        # FusionAI Companion rendszer
│   ├── config/                 # Konfiguráció
│   ├── workflows/              # n8n workflow-ok
│   ├── local-stack/            # Helyi AI infrastruktúra
│   ├── vtuber/                 # VTuber komponensek
│   └── main.py                 # Fő alkalmazás
├── FusionAI-Companion/         # Másolat (archivált)
├── FusionAI-Companion-1/       # Másolat (archivált)
├── .env                        # Környezeti változók
├── docker-compose.yml          # Docker szolgáltatások
├── requirements.txt            # Fő függőségek
└── README.md                   # Projekt leírás
```

## Key Components

### 1. GarvisNeuralMind_v2

- **Cél**: AI-alapú rendszer modern nyelvi modellekkel
- **Fő funkciók**: Voice interaction, fine-tuning, böngészővezérlés
- **Technológiák**: FastAPI, WebSocket, Discord bot

### 2. FusionAI-Companion0

- **Cél**: Egyesített AI-ügynök és kódasszisztens
- **Fő funkciók**: Kódgenerálás, RAG, VTuber streaming
- **Technológiák**: Ollama, Supabase, Neo4j, n8n

## Development Workflow

### 1. Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd NeuralMind

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Docker Services

```bash
# Start all services
docker-compose -f FusionAI-Companion0/docker-compose.yml up -d

# Check services
docker-compose ps
```

### 3. Development

```bash
# Start FusionAI Companion
python FusionAI-Companion0/main.py

# Start GarvisNeuralMind
python GarvisNeuralMind_v2/src/main.py

# Run tests
python -m pytest tests/ -v

# Format code
black .
flake8 .
```

## Service Ports

| Service | Port | Description |
|---------|------|-------------|
| FusionAI API | 8888 | Fő webes API |
| Open WebUI | 3000 | AI chat felület |
| n8n Workflows | 5678 | Workflow automatizálás |
| Langfuse | 3001 | Monitoring |
| Neo4j Browser | 7474 | Graph adatbázis |
| Supabase | 5432 | PostgreSQL adatbázis |
| Redis | 6379 | Cache |
| SearXNG | 8080 | Keresőmotor |
| Crawl4AI | 8000 | Web crawling |
| Whisper | 8081 | Speech recognition |

## Configuration

### Environment Variables

- `SUPABASE_URL`: Supabase projekt URL
- `OPENAI_API_KEY`: OpenAI API kulcs
- `ANTHROPIC_API_KEY`: Anthropic API kulcs
- `OLLAMA_URL`: Ollama szolgáltatás URL

### Feature Flags

- `ENABLE_VTUBER`: VTuber funkciók engedélyezése
- `ENABLE_VOICE_INTERACTION`: Hangalapú interakció
- `ENABLE_STREAMING`: Streaming funkciók
- `ENABLE_CODE_GENERATION`: Kódgenerálás
- `ENABLE_WORKFLOW_AUTOMATION`: Workflow automatizálás

## Monitoring and Debugging

### Health Checks

```bash
# System health check
python FusionAI-Companion0/health_check.py

# Quick demo
python FusionAI-Companion0/quickstart.py

# Full test suite
python FusionAI-Companion0/test_suite.py
```

### Logs

- Application logs: `logs/` directory
- Docker logs: `docker-compose logs <service-name>`
- Langfuse monitoring: <http://localhost:3001>

## Deployment

### Production

```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Environment variables
cp .env.example .env
# Edit .env with production values
```

### Development

```bash
# Quick start
./start.sh  # Linux/Mac
# or
.\start.ps1 # Windows

# Manual start
make dev
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test
4. Format code: `make format`
5. Run tests: `make test`
6. Submit pull request

## Troubleshooting

### Common Issues

1. **Port conflicts**: Check if ports are already in use
2. **Docker issues**: Restart Docker daemon
3. **Python dependencies**: Recreate virtual environment
4. **Database connection**: Check environment variables

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export DEBUG=true

# Start with debug
python -u main.py
```
