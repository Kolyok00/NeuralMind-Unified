#!/bin/bash

echo "🔧 Running post-create setup for NeuralMind Dev Container..."

# Update system packages
sudo apt-get update

# Install additional development tools if needed
sudo apt-get install -y \
    htop \
    tree \
    curl \
    wget \
    jq \
    net-tools

# Set up Python environment
echo "🐍 Setting up Python environment..."
python3 -m pip install --user --upgrade pip setuptools wheel

# Install NeuralMind dependencies
if [ -f "/workspace/d_drive/projects/NeuralMind-Unified/requirements.txt" ]; then
    echo "📦 Installing NeuralMind dependencies..."
    python3 -m pip install --user -r /workspace/d_drive/projects/NeuralMind-Unified/requirements.txt
fi

# Set up git configuration
echo "🔧 Setting up git configuration..."
git config --global --add safe.directory /workspace
git config --global init.defaultBranch main

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p /workspace/d_drive/projects/NeuralMind-Unified/{logs,data,cache,models,uploads}

# Set proper permissions
sudo chown -R ubuntu:ubuntu /workspace/d_drive/projects/NeuralMind-Unified

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Set up NeuralMind bash configuration
echo "⚡ Setting up NeuralMind bash configuration..."
if [ ! -f ~/.bashrc_neuralmind ]; then
    cat > ~/.bashrc_neuralmind << 'EOF'
#!/bin/bash
# NeuralMind Development Environment

# Set NeuralMind environment
export NEURALMIND_PATH="/workspace/d_drive/projects/NeuralMind-Unified"
export PYTHONPATH="$NEURALMIND_PATH"
export NEURALMIND_ENV="development"
export NEURALMIND_CONFIG="$NEURALMIND_PATH/config/main.json"

# NeuralMind aliases
alias neuralmind='cd "$NEURALMIND_PATH" && python3 main.py'
alias mcp='cd "$NEURALMIND_PATH" && python3 -m neuralmind.mcp_server'
alias neural-cd='cd "$NEURALMIND_PATH"'
alias neural-status='cd "$NEURALMIND_PATH" && python3 main.py --help'
alias neural-test='cd "$NEURALMIND_PATH" && python3 -c "import neuralmind; print(\"NeuralMind module loaded successfully\")"'

# Development aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias grep='grep --color=auto'

# Git aliases
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline'

# Python aliases
alias py='python3'
alias pip='pip3'
alias venv='python3 -m venv'

# Docker aliases
alias dps='docker ps'
alias dimg='docker images'
alias dlog='docker logs'
alias dexec='docker exec -it'
alias dcompose='docker-compose'

# Docker Compose profiles
alias neural-start='cd "$NEURALMIND_PATH" && docker-compose -f docker-compose.dev.yml up -d'
alias neural-stop='cd "$NEURALMIND_PATH" && docker-compose -f docker-compose.dev.yml down'
alias neural-ai='cd "$NEURALMIND_PATH" && docker-compose -f docker-compose.dev.yml --profile ai-services up -d'
alias neural-db='cd "$NEURALMIND_PATH" && docker-compose -f docker-compose.dev.yml --profile database-services up -d'
alias neural-workflow='cd "$NEURALMIND_PATH" && docker-compose -f docker-compose.dev.yml --profile workflow-services up -d'

# JSON processing functions
json_validate() {
    if [ $# -eq 0 ]; then
        echo "Usage: json_validate <file.json>"
        return 1
    fi
    python3 -c "import json; json.load(open('$1'))" 2>/dev/null && echo "✅ Valid JSON" || echo "❌ Invalid JSON"
}

json_format() {
    if [ $# -eq 0 ]; then
        echo "Usage: json_format <file.json>"
        return 1
    fi
    python3 -c "import json; print(json.dumps(json.load(open('$1')), indent=2))"
}

# NeuralMind help function
neuralmind-help() {
    echo "🧠 NeuralMind Development Commands:"
    echo ""
    echo "📱 Application:"
    echo "  neuralmind      - Start NeuralMind application"
    echo "  mcp             - Start MCP server"
    echo "  neural-cd       - Go to NeuralMind directory"
    echo "  neural-status   - Check NeuralMind status"
    echo "  neural-test     - Test NeuralMind module import"
    echo ""
    echo "🐳 Docker Services:"
    echo "  neural-start    - Start development services"
    echo "  neural-stop     - Stop development services"
    echo "  neural-ai       - Start AI services (Ollama, OpenWebUI)"
    echo "  neural-db       - Start database services (Postgres, Redis, Neo4j)"
    echo "  neural-workflow - Start workflow services (n8n)"
    echo ""
    echo "🔧 Development:"
    echo "  json_validate   - Validate JSON file"
    echo "  json_format     - Format JSON file"
    echo ""
    echo "📁 Paths:"
    echo "  NeuralMind: $NEURALMIND_PATH"
    echo "  Python: $PYTHONPATH"
    echo "  Environment: $NEURALMIND_ENV"
}

# Welcome message
echo "🧠 NeuralMind Development Environment Ready!"
echo "📍 Use 'neuralmind-help' for available commands"
echo "🐳 Use 'neural-start' to start development services"
EOF
fi

# Add NeuralMind configuration to bashrc
if ! grep -q "source ~/.bashrc_neuralmind" ~/.bashrc 2>/dev/null; then
    echo "" >> ~/.bashrc
    echo "# NeuralMind Development Environment" >> ~/.bashrc
    echo "if [ -f ~/.bashrc_neuralmind ]; then" >> ~/.bashrc
    echo "    source ~/.bashrc_neuralmind" >> ~/.bashrc
    echo "fi" >> ~/.bashrc
fi

echo "✅ Post-create setup completed!"
echo ""
echo "🚀 NeuralMind Development Container is ready!"
echo "📍 Use 'neuralmind-help' for available commands"
echo "🐳 Use 'neural-start' to start development services"