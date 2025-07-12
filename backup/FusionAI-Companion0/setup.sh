#!/bin/bash

# FusionAI Companion - Setup Script
# This script initializes the FusionAI Companion project with all necessary components

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check system requirements
check_requirements() {
    print_info "Checking system requirements..."

    # Check Docker
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check Docker Compose
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    # Check Git
    if ! command_exists git; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi

    # Check if running from correct directory
    if [ ! -f "docker-compose.yml" ]; then
        print_error "Please run this script from the FusionAI-Companion root directory."
        exit 1
    fi

    print_success "System requirements check passed!"
}

# Function to setup environment file
setup_environment() {
    print_info "Setting up environment configuration..."

    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Created .env file from template"
            print_warning "Please edit .env file with your API keys and configuration"
        else
            print_error ".env.example file not found"
            exit 1
        fi
    else
        print_info ".env file already exists, skipping..."
    fi
}

# Function to create necessary directories
create_directories() {
    print_info "Creating necessary directories..."

    directories=(
        "data"
        "logs"
        "models"
        "audio"
        "searxng"
        "supabase/migrations"
    )

    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        fi
    done
}

# Function to initialize git submodules
setup_submodules() {
    print_info "Setting up git submodules..."

    # Initialize submodules if they don't exist
    submodules=(
        "https://github.com/opencode-ai/opencode:core-agent"
        "https://github.com/coleam00/mcp-crawl4ai-rag:ingest"
        "https://github.com/coleam00/local-ai-packaged:local-stack"
        "https://github.com/coleam00/ottomator-agents:workflows"
        "https://github.com/ExpiredPopsicle/SnekStudio:vtuber"
    )

    for submodule in "${submodules[@]}"; do
        IFS=':' read -r repo_url local_path <<< "$submodule"

        if [ ! -d "$local_path/.git" ]; then
            print_info "Adding submodule: $local_path"
            git submodule add "$repo_url" "$local_path" || true
        else
            print_info "Submodule $local_path already exists"
        fi
    done

    # Initialize and update submodules
    print_info "Initializing and updating submodules..."
    git submodule init
    git submodule update --recursive

    print_success "Git submodules setup complete!"
}

# Function to pull Docker images
pull_docker_images() {
    print_info "Pulling Docker images..."

    if command_exists docker-compose; then
        docker-compose pull
    else
        docker compose pull
    fi

    print_success "Docker images pulled successfully!"
}

# Function to start core services
start_core_services() {
    print_info "Starting core services..."

    # Start databases first
    core_services="ollama supabase-db neo4j redis"

    if command_exists docker-compose; then
        docker-compose up -d $core_services
    else
        docker compose up -d $core_services
    fi

    print_info "Waiting for databases to initialize..."
    sleep 30

    print_success "Core services started!"
}

# Function to start all services
start_all_services() {
    print_info "Starting all services..."

    if command_exists docker-compose; then
        docker-compose up -d
    else
        docker compose up -d
    fi

    print_success "All services started!"
}

# Function to download essential AI models
download_models() {
    print_info "Downloading essential AI models..."

    # Wait for Ollama to be ready
    print_info "Waiting for Ollama to be ready..."
    timeout=60
    while ! docker exec fusionai-ollama ollama list >/dev/null 2>&1; do
        sleep 5
        timeout=$((timeout - 5))
        if [ $timeout -le 0 ]; then
            print_warning "Ollama not ready, skipping model download"
            return
        fi
    done

    # Download essential models
    models=(
        "qwen2:7b"
        "mistral:7b"
        "deepseek-coder:6.7b"
        "nomic-embed-text"
    )

    for model in "${models[@]}"; do
        print_info "Downloading model: $model"
        docker exec fusionai-ollama ollama pull "$model" || print_warning "Failed to download $model"
    done

    print_success "Model download complete!"
}

# Function to run health check
health_check() {
    print_info "Running health check..."

    services=(
        "fusionai-ollama:11434"
        "fusionai-open-webui:8080"
        "fusionai-n8n:5678"
        "fusionai-neo4j:7474"
        "fusionai-supabase-db:5432"
    )

    for service in "${services[@]}"; do
        IFS=':' read -r container_name port <<< "$service"
        if docker ps --format 'table {{.Names}}' | grep -q "$container_name"; then
            print_success "✓ $container_name is running"
        else
            print_warning "⚠ $container_name is not running"
        fi
    done
}

# Function to display access information
show_access_info() {
    print_info "FusionAI Companion is ready!"
    echo
    echo -e "${GREEN}Access URLs:${NC}"
    echo -e "  • Open WebUI (Chat):     ${BLUE}http://localhost:3000${NC}"
    echo -e "  • n8n Workflows:         ${BLUE}http://localhost:5678${NC}"
    echo -e "  • Langfuse Monitoring:   ${BLUE}http://localhost:3001${NC}"
    echo -e "  • Neo4j Browser:         ${BLUE}http://localhost:7474${NC}"
    echo -e "  • SearXNG Search:        ${BLUE}http://localhost:8080${NC}"
    echo
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  1. Edit .env file with your API keys"
    echo "  2. Open Open WebUI to start chatting with AI"
    echo "  3. Configure n8n workflows for automation"
    echo "  4. Explore the documentation in each module directory"
    echo
    echo -e "${BLUE}Commands:${NC}"
    echo "  • Stop all services:     docker-compose down"
    echo "  • View logs:             docker-compose logs -f"
    echo "  • Restart services:      docker-compose restart"
    echo
}

# Generate a load test script
@testing /generateLoadTest

# Run a load test in Azure
@testing /runLoadTestInAzure

# Run a load test locally
@testing /runLoadTestLocally

# Validate your load test configuration
@testing /validateLoadTestConfig

# Main execution
main() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  FusionAI Companion Setup Script${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo

    check_requirements
    setup_environment
    create_directories
    setup_submodules
    pull_docker_images
    start_core_services
    start_all_services
    download_models
    health_check
    show_access_info

    print_success "Setup complete! FusionAI Companion is ready to use."
}

# Handle script arguments
case "${1:-setup}" in
    "setup"|"")
        main
        ;;
    "health")
        health_check
        ;;
    "models")
        download_models
        ;;
    "start")
        start_all_services
        ;;
    "stop")
        print_info "Stopping all services..."
        if command_exists docker-compose; then
            docker-compose down
        else
            docker compose down
        fi
        print_success "All services stopped!"
        ;;
    *)
        echo "Usage: $0 [setup|health|models|start|stop]"
        echo "  setup  - Full setup (default)"
        echo "  health - Check service health"
        echo "  models - Download AI models"
        echo "  start  - Start all services"
        echo "  stop   - Stop all services"
        exit 1
        ;;
esac
