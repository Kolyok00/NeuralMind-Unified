"""
NeuralMind Core Module
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Project information
PROJECT_NAME = "NeuralMind Unified"
PROJECT_VERSION = "1.0.0"
PROJECT_PATH = "/workspace/d_drive/projects/NeuralMind-Unified"
PROJECT_DESCRIPTION = "AI Companion Ecosystem with code generation, VTuber, and agent capabilities"

# Core configuration
DEFAULT_CONFIG = {
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
    },
    "mcp": {
        "enabled": True,
        "port": 3000,
        "host": "localhost"
    }
}


def get_project_root() -> Path:
    """Get project root directory"""
    return Path(PROJECT_PATH)


def get_config_path() -> Path:
    """Get configuration file path"""
    return get_project_root() / "config" / "main.json"


def get_logs_path() -> Path:
    """Get logs directory path"""
    return get_project_root() / "logs"


def get_data_path() -> Path:
    """Get data directory path"""
    return get_project_root() / "data"


def get_models_path() -> Path:
    """Get models directory path"""
    return get_project_root() / "models"


def ensure_directories():
    """Ensure all necessary directories exist"""
    directories = [
        get_logs_path(),
        get_data_path(),
        get_models_path(),
        get_project_root() / "cache",
        get_project_root() / "uploads"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def get_environment_info() -> Dict[str, Any]:
    """Get current environment information"""
    return {
        "python_version": sys.version,
        "platform": sys.platform,
        "project_path": PROJECT_PATH,
        "working_directory": os.getcwd(),
        "environment_variables": {
            "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
            "NEURALMIND_ENV": os.environ.get("NEURALMIND_ENV", "development"),
            "NEURALMIND_CONFIG": os.environ.get("NEURALMIND_CONFIG", "")
        }
    }


class NeuralMindCore:
    """Core NeuralMind functionality"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or DEFAULT_CONFIG
        self.project_root = get_project_root()
        
    def initialize(self):
        """Initialize core components"""
        ensure_directories()
        
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "project": {
                "name": PROJECT_NAME,
                "version": PROJECT_VERSION,
                "path": PROJECT_PATH,
                "description": PROJECT_DESCRIPTION
            },
            "environment": get_environment_info(),
            "config": self.config,
            "status": "active"
        }


# Export core functionality
__all__ = [
    "PROJECT_NAME",
    "PROJECT_VERSION", 
    "PROJECT_PATH",
    "PROJECT_DESCRIPTION",
    "DEFAULT_CONFIG",
    "get_project_root",
    "get_config_path",
    "get_logs_path",
    "get_data_path",
    "get_models_path",
    "ensure_directories",
    "get_environment_info",
    "NeuralMindCore"
]