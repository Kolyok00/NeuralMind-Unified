#!/bin/bash
set -e

echo "🚀 Starting NeuralMind Development Container..."

# Set up NeuralMind environment
export PYTHONPATH="/workspace/d_drive/projects/NeuralMind-Unified"
export NEURALMIND_ENV="development"
export NEURALMIND_CONFIG="/workspace/d_drive/projects/NeuralMind-Unified/config/main.json"

# Create necessary directories
mkdir -p /workspace/d_drive/projects/NeuralMind-Unified/{logs,data,cache,models,uploads}

# Set up git if not configured
if [ ! -f ~/.gitconfig ]; then
    git config --global user.name "NeuralMind Developer"
    git config --global user.email "dev@neuralmind.local"
    git config --global init.defaultBranch main
fi

# Install/update NeuralMind dependencies if requirements.txt exists
if [ -f "/workspace/d_drive/projects/NeuralMind-Unified/requirements.txt" ]; then
    echo "📦 Installing NeuralMind dependencies..."
    pip3 install --user -r /workspace/d_drive/projects/NeuralMind-Unified/requirements.txt
fi

# Set up bash aliases for NeuralMind
if [ ! -f ~/.bashrc ] || ! grep -q "neuralmind" ~/.bashrc; then
    echo "⚡ Setting up NeuralMind bash aliases..."
    cat >> ~/.bashrc << 'EOF'

# NeuralMind Development Aliases
export NEURALMIND_PATH="/workspace/d_drive/projects/NeuralMind-Unified"
export PYTHONPATH="$NEURALMIND_PATH"
export NEURALMIND_ENV="development"

alias neuralmind='cd "$NEURALMIND_PATH" && python3 main.py'
alias mcp='cd "$NEURALMIND_PATH" && python3 -m neuralmind.mcp_server'
alias neural-cd='cd "$NEURALMIND_PATH"'
alias neural-status='cd "$NEURALMIND_PATH" && python3 main.py --help'
alias neural-test='cd "$NEURALMIND_PATH" && python3 -c "import neuralmind; print(\"NeuralMind module loaded successfully\")"'

# Development aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline'
alias py='python3'
alias pip='pip3'

# Docker aliases
alias dps='docker ps'
alias dimg='docker images'
alias dlog='docker logs'
alias dexec='docker exec -it'

# NeuralMind help function
neuralmind-help() {
    echo "🧠 NeuralMind Development Commands:"
    echo "  neuralmind      - Start NeuralMind application"
    echo "  mcp             - Start MCP server"
    echo "  neural-cd       - Go to NeuralMind directory"
    echo "  neural-status   - Check NeuralMind status"
    echo "  neural-test     - Test NeuralMind module import"
    echo ""
    echo "📁 Current NeuralMind path: $NEURALMIND_PATH"
    echo "🐍 Python path: $PYTHONPATH"
    echo "🔧 Environment: $NEURALMIND_ENV"
}

echo "🧠 NeuralMind Development Environment Ready!"
echo "📍 Use 'neuralmind-help' for available commands"
EOF
fi

# Source bashrc to load aliases
source ~/.bashrc 2>/dev/null || true

# Check Docker socket access
if [ -S /var/run/docker-host.sock ]; then
    echo "🐳 Docker socket mounted successfully"
else
    echo "⚠️  Docker socket not found - Docker commands may not work"
fi

# Print status
echo "✅ NeuralMind Development Container is ready!"
echo "📍 Workspace: /workspace"
echo "🧠 NeuralMind Project: /workspace/d_drive/projects/NeuralMind-Unified"
echo "🐍 Python: $(python3 --version)"
echo "🔧 Environment: $NEURALMIND_ENV"
echo ""
echo "🚀 Available services:"
echo "  - NeuralMind Web UI: http://localhost:8888"
echo "  - Open WebUI: http://localhost:3000"
echo "  - n8n Workflows: http://localhost:5678"
echo "  - Ollama API: http://localhost:11434"
echo ""
echo "💡 Use 'neuralmind-help' for development commands"

# Execute the main command
exec "$@"