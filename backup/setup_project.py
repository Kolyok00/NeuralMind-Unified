#!/usr/bin/env python3
"""
NeuralMind Project Setup Script
Automatically sets up the project environment and installs dependencies
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(command, check=True, shell=True):
    """Run a command and return the result"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=shell, 
            check=check, 
            capture_output=True, 
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("Error: Python 3.9 or higher is required")
        sys.exit(1)
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

def install_dependencies():
    """Install project dependencies"""
    print("Installing core dependencies...")
    
    # Try to install with --break-system-packages if needed
    try:
        run_command("pip3 install --upgrade pip setuptools wheel")
    except:
        try:
            run_command("pip3 install --break-system-packages --upgrade pip setuptools wheel")
        except:
            print("Warning: Could not upgrade pip")
    
    # Install core dependencies
    core_deps = [
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0", 
        "pydantic>=2.4.2",
        "httpx>=0.25.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.1",
        "loguru>=0.7.2"
    ]
    
    for dep in core_deps:
        try:
            run_command(f"pip3 install '{dep}'")
        except:
            try:
                run_command(f"pip3 install --break-system-packages '{dep}'")
            except:
                print(f"Warning: Could not install {dep}")

def create_directories():
    """Create necessary directories"""
    dirs = [
        "logs",
        "config", 
        "data",
        "uploads",
        "models",
        "cache"
    ]
    
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"Created directory: {dir_name}")

def create_config_files():
    """Create default configuration files"""
    
    # Create main.json config
    config_path = Path("config/main.json")
    if not config_path.exists():
        default_config = {
            "core_agent": {
                "enabled": True,
                "provider": "ollama",
                "model": "qwen2:7b",
                "max_tokens": 4096,
                "temperature": 0.1
            },
            "embedding": {
                "enabled": True,
                "model": "nomic-embed-text",
                "chunk_size": 1000,
                "chunk_overlap": 200
            },
            "vtuber": {
                "enabled": False,
                "model_path": "vtuber/models/default.vrm",
                "voice_enabled": True,
                "animation_enabled": True
            },
            "workflows": {
                "enabled": True,
                "auto_start": ["health_check", "model_warmup"],
                "n8n_url": "http://localhost:5678"
            },
            "web_ui": {
                "enabled": True,
                "host": "0.0.0.0",
                "port": 8888,
                "cors_enabled": True
            },
            "monitoring": {
                "enabled": True,
                "langfuse_enabled": True,
                "metrics_interval": 60
            }
        }
        
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        print(f"Created config file: {config_path}")
    
    # Create .env file if it doesn't exist
    env_path = Path(".env")
    if not env_path.exists():
        env_content = """# NeuralMind Environment Variables

# API Keys (add your own)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GROQ_API_KEY=your_groq_key_here

# Database
DATABASE_URL=sqlite:///./data/neuralmind.db
REDIS_URL=redis://localhost:6379

# Web UI
WEB_HOST=0.0.0.0
WEB_PORT=8888

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/neuralmind.log

# Features
ENABLE_VTUBER=false
ENABLE_WORKFLOWS=true
ENABLE_MONITORING=true
"""
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"Created environment file: {env_path}")

def create_startup_script():
    """Create a simple startup script"""
    script_content = """#!/bin/bash
# NeuralMind Startup Script

echo "Starting NeuralMind..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed"
    exit 1
fi

# Run the main application
python3 FusionAI-Companion0/main.py "$@"
"""
    
    script_path = Path("start_neuralmind.sh")
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(script_path, 0o755)
    print(f"Created startup script: {script_path}")

def main():
    """Main setup function"""
    print("=" * 50)
    print("NeuralMind Project Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Create directories
    create_directories()
    
    # Install dependencies
    install_dependencies()
    
    # Create config files
    create_config_files()
    
    # Create startup script
    create_startup_script()
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Edit config/main.json to configure your settings")
    print("2. Add your API keys to the .env file")
    print("3. Run: ./start_neuralmind.sh")
    print("4. Or run: python3 FusionAI-Companion0/main.py")
    print("\nWeb interface will be available at: http://localhost:8888")

if __name__ == "__main__":
    main()