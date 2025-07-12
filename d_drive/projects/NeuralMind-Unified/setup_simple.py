#!/usr/bin/env python3
"""
FusionAI Companion Setup Script
Simple installation and configuration helper
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path


def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("           FusionAI Companion Setup")
    print("      Unified AI Agent & VTuber System")
    print("=" * 60)


def check_python():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print("✅ Python version OK")
    return True


def install_requirements():
    """Install Python requirements"""
    print("\n📦 Installing requirements...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
        )
        print("✅ Requirements installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False


def setup_environment():
    """Setup environment file"""
    print("\n⚙️ Setting up environment...")

    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file")
    elif env_file.exists():
        print("📄 .env file already exists")
    else:
        print("⚠️ No .env.example found")

    return True


def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")

    dirs = ["logs", "data", "uploads", "static"]
    for directory in dirs:
        Path(directory).mkdir(exist_ok=True)
        print(f"  📁 {directory}")

    print("✅ Directories created")
    return True


def setup_config():
    """Setup basic configuration"""
    print("\n🔧 Setting up configuration...")

    config_dir = Path("config")
    config_file = config_dir / "main.json"

    if not config_file.exists():
        config_dir.mkdir(exist_ok=True)

        # Basic default config
        config = {
            "core_agent": {"enabled": True, "provider": "ollama", "model": "qwen2:7b"},
            "embedding": {"enabled": True, "model": "nomic-embed-text"},
            "vtuber": {"enabled": False},
            "workflows": {"enabled": True, "n8n_url": "http://localhost:5678"},
            "web_ui": {"enabled": True, "host": "0.0.0.0", "port": 8888},
        }

        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)

        print("✅ Configuration created")
    else:
        print("📄 Configuration already exists")

    return True


def show_next_steps():
    """Show next steps"""
    print("\n🎉 Setup complete!")
    print("\n📝 Next steps:")
    print("1. Edit .env with your API keys")
    print("2. Start services: python main.py")
    print("3. Visit: http://localhost:8888")
    print("4. API docs: http://localhost:8888/docs")
    print("5. Run demo: python quickstart.py")


def main():
    """Main setup function"""
    print_banner()

    # Check prerequisites
    if not check_python():
        sys.exit(1)

    # Run setup steps
    steps = [install_requirements, setup_environment, create_directories, setup_config]

    for step in steps:
        if not step():
            print(f"\n❌ Setup failed at {step.__name__}")
            sys.exit(1)

    show_next_steps()
    print("\n✅ Setup completed successfully!")


if __name__ == "__main__":
    main()
