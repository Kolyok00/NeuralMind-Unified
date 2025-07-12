#!/bin/bash

echo "🚀 Running post-start setup for NeuralMind Dev Container..."

# Source the NeuralMind environment
if [ -f ~/.bashrc_neuralmind ]; then
    source ~/.bashrc_neuralmind
fi

# Check if we're in the correct directory
if [ ! -d "/workspace/d_drive/projects/NeuralMind-Unified" ]; then
    echo "⚠️  NeuralMind project directory not found!"
    exit 1
fi

# Navigate to NeuralMind directory
cd /workspace/d_drive/projects/NeuralMind-Unified

# Check Docker availability
if command -v docker &> /dev/null; then
    echo "🐳 Docker is available"
    docker --version
else
    echo "⚠️  Docker not available"
fi

# Check Python environment
echo "🐍 Python environment:"
python3 --version
pip3 --version

# Test NeuralMind module import
echo "🧪 Testing NeuralMind module..."
if python3 -c "import neuralmind; print('✅ NeuralMind module loaded successfully')" 2>/dev/null; then
    echo "✅ NeuralMind module is working"
else
    echo "⚠️  NeuralMind module not found - may need to install dependencies"
fi

# Check for running services
echo "🔍 Checking for running services..."
if command -v docker &> /dev/null; then
    running_containers=$(docker ps --format "table {{.Names}}\t{{.Ports}}" | grep -E "(neuralmind|ollama|n8n)" || echo "No NeuralMind containers running")
    echo "Running containers:"
    echo "$running_containers"
fi

# Display useful information
echo ""
echo "✅ NeuralMind Development Environment is ready!"
echo ""
echo "📍 Current directory: $(pwd)"
echo "🧠 NeuralMind project: /workspace/d_drive/projects/NeuralMind-Unified"
echo ""
echo "🚀 Quick start commands:"
echo "  neuralmind-help     - Show all available commands"
echo "  neural-start        - Start development services"
echo "  neuralmind          - Start NeuralMind application"
echo "  mcp                 - Start MCP server"
echo ""
echo "🌐 Service URLs (when running):"
echo "  - NeuralMind Web UI: http://localhost:8888"
echo "  - Open WebUI: http://localhost:3000"
echo "  - n8n Workflows: http://localhost:5678"
echo "  - Ollama API: http://localhost:11434"
echo ""
echo "💡 Tip: Use 'neural-start' to start all development services"