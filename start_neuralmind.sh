#!/bin/bash
# NeuralMind Startup Script

echo "Starting NeuralMind..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed"
    exit 1
fi

# Run the main application
python3 FusionAI-Companion0/main.py "$@"
