#!/bin/bash

# NeuralMind Startup Script for Linux/WSL2

echo "🚀 Starting NeuralMind AI Ecosystem..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "�� Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Start Docker services
echo "🐳 Starting Docker services..."
docker-compose -f FusionAI-Companion0/docker-compose.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Start the main application
echo "🎯 Starting NeuralMind..."
python FusionAI-Companion0/main.py 