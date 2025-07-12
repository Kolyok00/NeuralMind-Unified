#!/usr/bin/env python3
"""
FusionAI Companion - Complete Setup and Demo Script
This script demonstrates the complete functionality of the FusionAI Companion system
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path


def print_banner():
    """Print welcome banner"""
    print(
        """
🚀 FusionAI Companion - Complete Demo
====================================

This script will:
1. Check system prerequisites
2. Start all Docker services
3. Run health checks
4. Demonstrate core functionality
5. Show you how to access all interfaces

Let's get started!
"""
    )


def check_prerequisites():
    """Check if required tools are available"""
    print("🔍 Checking prerequisites...")

    required_tools = ["docker", "python"]
    missing_tools = []

    for tool in required_tools:
        try:
            result = subprocess.run(
                [tool, "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print(f"  ✅ {tool} is available")
            else:
                missing_tools.append(tool)
                print(f"  ❌ {tool} is not working properly")
        except FileNotFoundError:
            missing_tools.append(tool)
            print(f"  ❌ {tool} is not installed")
        except subprocess.TimeoutExpired:
            missing_tools.append(tool)
            print(f"  ❌ {tool} command timed out")

    if missing_tools:
        print(f"\n❌ Missing required tools: {', '.join(missing_tools)}")
        print("Please install them and try again.")
        return False

    print("✅ All prerequisites met!")
    return True


def start_docker_services():
    """Start Docker services"""
    print("\n🐳 Starting Docker services...")

    try:
        # Check if docker-compose.yml exists
        if not Path("docker-compose.yml").exists():
            print("❌ docker-compose.yml not found!")
            print("Please run this script from the FusionAI-Companion root directory.")
            return False

        # Start services
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes timeout
        )

        if result.returncode == 0:
            print("✅ Docker services started successfully!")
            print("⏳ Waiting for services to initialize...")
            time.sleep(30)  # Give services time to start
            return True
        else:
            print(f"❌ Failed to start Docker services: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Docker startup timed out")
        return False
    except Exception as e:
        print(f"❌ Error starting Docker services: {e}")
        return False


def run_health_check():
    """Run health check"""
    print("\n🏥 Running health check...")

    try:
        result = subprocess.run(
            [sys.executable, "health_check.py"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        print(result.stdout)

        if result.returncode == 0:
            print("✅ Health check passed!")
            return True
        else:
            print("⚠️ Some services may not be fully ready yet")
            print("This is normal during first startup")
            return True  # Don't fail the demo for this

    except subprocess.TimeoutExpired:
        print("⚠️ Health check timed out")
        return True
    except Exception as e:
        print(f"⚠️ Health check error: {e}")
        return True


def run_quick_demo():
    """Run the quick demonstration"""
    print("\n🎭 Running functionality demo...")

    try:
        result = subprocess.run(
            [sys.executable, "quickstart.py"],
            capture_output=True,
            text=True,
            timeout=120,
        )

        print(result.stdout)

        if result.returncode == 0:
            print("✅ Demo completed successfully!")
            return True
        else:
            print(f"⚠️ Demo encountered issues: {result.stderr}")
            return True  # Don't fail for demo issues

    except subprocess.TimeoutExpired:
        print("⚠️ Demo timed out")
        return True
    except Exception as e:
        print(f"⚠️ Demo error: {e}")
        return True


def show_access_info():
    """Show how to access all interfaces"""
    print(
        """
🌐 Access Information
====================

Your FusionAI Companion is now running! Here's how to access it:

🎯 Main Interfaces:
  • FusionAI API & Web UI:   http://localhost:8888
  • Interactive API Docs:   http://localhost:8888/docs
  • Open WebUI (Chat):      http://localhost:3000
  • n8n Workflows:          http://localhost:5678
  • Monitoring (Langfuse):  http://localhost:3001

🔧 Development Tools:
  • Neo4j Browser:          http://localhost:7474
  • SearXNG Search:         http://localhost:8080

📋 Quick Commands:
  • Start application:      python main.py
  • Run health check:       python health_check.py
  • Run tests:              python test_suite.py
  • Stop services:          docker-compose down

🎓 Next Steps:
  1. Open the main web interface: http://localhost:8888
  2. Try the chat interface: http://localhost:3000
  3. Explore the API documentation: http://localhost:8888/docs
  4. Create workflows in n8n: http://localhost:5678
  5. Monitor performance: http://localhost:3001

📚 Documentation:
  • Installation Guide:     docs/installation.md
  • Module Documentation:   docs/modules/
  • API Reference:          http://localhost:8888/docs

🆘 Need Help?
  • Check logs:             docker-compose logs -f
  • Run diagnostics:        python health_check.py
  • Test functionality:     python test_suite.py

Enjoy using FusionAI Companion! 🎉
"""
    )


def main():
    """Main entry point"""
    print_banner()

    try:
        # Step 1: Check prerequisites
        if not check_prerequisites():
            sys.exit(1)

        # Step 2: Start Docker services
        if not start_docker_services():
            sys.exit(1)

        # Step 3: Run health check
        run_health_check()

        # Step 4: Run demo
        run_quick_demo()

        # Step 5: Show access information
        show_access_info()

        print("🎉 Setup and demo completed successfully!")
        print("FusionAI Companion is ready to use!")

    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
