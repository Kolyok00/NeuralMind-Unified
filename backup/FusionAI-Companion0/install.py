#!/usr/bin/env python3
"""
FusionAI Companion Installation and Setup Script
This script helps users set up the FusionAI Companion system step by step
"""

import asyncio
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict

import httpx


class FusionAIInstaller:
    """Installation and setup manager for FusionAI Companion"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_path = self.project_root / "config" / "main.json"
        self.env_path = self.project_root / ".env"
        self.env_example_path = self.project_root / ".env.example"

    def print_banner(self):
        """Print welcome banner"""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║                    FusionAI Companion                    ║
║                  Installation & Setup                    ║
║                                                           ║
║  Unified AI Agent, Code Assistant & VTuber Ecosystem     ║
╚═══════════════════════════════════════════════════════════╝
        """
        print(banner)

    def check_prerequisites(self) -> Dict[str, bool]:
        """Check system prerequisites"""
        print("🔍 Checking prerequisites...")

        checks = {
            "Python 3.8+": sys.version_info >= (3, 8),
            "pip": shutil.which("pip") is not None,
            "git": shutil.which("git") is not None,
            "docker": shutil.which("docker") is not None,
            "docker-compose": (
                shutil.which("docker-compose") is not None
                or shutil.which("docker") is not None
            ),
        }

        for name, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {name}")

        return checks

    def install_python_dependencies(self):
        """Install Python dependencies"""
        print("\n📦 Installing Python dependencies...")

        try:
            # Upgrade pip first
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True
            )

            # Install requirements
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                check=True,
            )
            print("✅ Python dependencies installed successfully!")

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False

        return True

    def setup_environment(self):
        """Set up environment configuration"""
        print("\n⚙️ Setting up environment configuration...")

        if not self.env_path.exists():
            if self.env_example_path.exists():
                shutil.copy(self.env_example_path, self.env_path)
                print("✅ Created .env file from template")
            else:
                print("❌ .env.example not found")
                return False
        else:
            print("📄 .env file already exists")

        return True

    def create_directories(self):
        """Create necessary directories"""
        print("\n📁 Creating necessary directories...")

        directories = [
            "logs",
            "data",
            "uploads",
            "static",
            "vtuber/models",
            "vtuber/audio",
            "vtuber/animations",
        ]

        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  📁 {directory}")

        print("✅ Directories created successfully!")
        return True

    def configure_services(self):
        """Interactive service configuration"""
        print("\n🔧 Configuring services...")

        # Load current config
        config = {}
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                config = json.load(f)

        # Core Agent Configuration
        print("\n🤖 Core Agent Configuration:")
        providers = ["ollama", "openai", "anthropic", "groq", "local"]
        print("Available AI providers:", ", ".join(providers))

        provider = input(
            f"Choose AI provider [{config.get('core_agent', {}).get('provider', 'ollama')}]: "
        ).strip()
        if provider:
            config.setdefault("core_agent", {})["provider"] = provider

        # Model configuration based on provider
        if provider == "ollama":
            model = input(
                f"Ollama model [{config.get('core_agent', {}).get('model', 'qwen2:7b')}]: "
            ).strip()
            if model:
                config["core_agent"]["model"] = model
        elif provider == "openai":
            model = input(
                f"OpenAI model [{config.get('core_agent', {}).get('model', 'gpt-4')}]: "
            ).strip()
            if model:
                config["core_agent"]["model"] = model

        # VTuber Configuration
        print("\n🎭 VTuber Configuration:")
        enable_vtuber = input("Enable VTuber features? [y/N]: ").strip().lower()
        config.setdefault("vtuber", {})["enabled"] = enable_vtuber in ["y", "yes"]

        # Workflow Configuration
        print("\n🔄 Workflow Configuration:")
        n8n_url = input(
            f"n8n URL [{config.get('workflows', {}).get('n8n_url', 'http://localhost:5678')}]: "
        ).strip()
        if n8n_url:
            config.setdefault("workflows", {})["n8n_url"] = n8n_url

        # Save configuration
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=4)

        print("✅ Configuration saved!")
        return True

    def start_docker_services(self):
        """Start Docker services"""
        print("\n🐳 Starting Docker services...")

        # Check if docker-compose.yml exists in local-stack
        local_stack_path = self.project_root / "local-stack"
        compose_file = local_stack_path / "docker-compose.yml"

        if compose_file.exists():
            try:
                os.chdir(local_stack_path)
                subprocess.run(["docker-compose", "up", "-d"], check=True)
                print("✅ Docker services started successfully!")
                os.chdir(self.project_root)
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to start Docker services: {e}")
                os.chdir(self.project_root)
                return False
        else:
            print("⚠️ No docker-compose.yml found in local-stack directory")
            return False

    async def test_services(self):
        """Test if services are running"""
        print("\n🧪 Testing services...")

        services = {
            "FusionAI API": "http://localhost:8888/health",
            "n8n": "http://localhost:5678",
            "Ollama": "http://localhost:11434",
        }

        results = {}
        async with httpx.AsyncClient(timeout=10.0) as client:
            for name, url in services.items():
                try:
                    response = await client.get(url)
                    results[name] = response.status_code == 200
                    status = "✅" if results[name] else "❌"
                    print(f"  {status} {name}")
                except Exception:
                    results[name] = False
                    print(f"  ❌ {name} (connection failed)")

        return results

    def show_next_steps(self):
        """Show next steps to the user"""
        print("\n🎉 Installation complete!")
        print("\n📝 Next steps:")
        print("1. Edit .env file with your API keys")
        print("2. Start the services:")
        print("   - Windows: start.bat or start.ps1")
        print("   - Linux/Mac: python main.py")
        print("3. Access the web interface at http://localhost:8888")
        print("4. View API documentation at http://localhost:8888/docs")
        print("5. Run quickstart demo: python quickstart.py")
        print("\n🔗 Useful links:")
        print("  - Web UI: http://localhost:8888")
        print("  - API Docs: http://localhost:8888/docs")
        print("  - n8n Workflows: http://localhost:5678")
        print("  - Health Check: python health_check.py")

    async def run_setup(self):
        """Run the complete setup process"""
        self.print_banner()

        # Check prerequisites
        prereqs = self.check_prerequisites()
        if not all(prereqs.values()):
            print(
                "\n❌ Some prerequisites are missing. Please install them and try again."
            )
            return False

        # Install dependencies
        if not self.install_python_dependencies():
            return False

        # Setup environment
        if not self.setup_environment():
            return False

        # Create directories
        if not self.create_directories():
            return False

        # Configure services
        if not self.configure_services():
            return False

        # Ask about Docker services
        start_docker = input("\nStart Docker services now? [Y/n]: ").strip().lower()
        if start_docker in ["", "y", "yes"]:
            self.start_docker_services()

        # Test services
        print("\nWould you like to test the services now?")
        test_now = (
            input("This will start FusionAI and test connections [Y/n]: ")
            .strip()
            .lower()
        )
        if test_now in ["", "y", "yes"]:
            # Start FusionAI in background for testing
            print("Starting FusionAI for testing...")
            await asyncio.sleep(2)  # Give services time to start
            await self.test_services()

        # Show next steps
        self.show_next_steps()
        return True


async def main():
    """Main entry point"""
    installer = FusionAIInstaller()

    try:
        success = await installer.run_setup()
        if success:
            print("\n✅ Setup completed successfully!")
        else:
            print("\n❌ Setup failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
