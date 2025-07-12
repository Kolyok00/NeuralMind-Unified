"""
NeuralMind Unified - AI Companion Ecosystem
"""

__version__ = "1.0.0"
__author__ = "NeuralMind Team"
__description__ = "Unified AI companion system with code generation, VTuber, and agent capabilities"

from .mcp_server import MCPServer
from .core import *

__all__ = [
    "MCPServer",
    "__version__",
    "__author__",
    "__description__"
]