#!/usr/bin/env python3
"""
Quick Start Script for FusionAI Companion
This script helps new users get started quickly with basic functionality
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from main import FusionAICompanion


async def demo_code_generation():
    """Demo code generation functionality"""
    print("🤖 Demo: Code Generation")
    print("-" * 40)

    # Initialize the companion
    companion = FusionAICompanion()
    await companion.initialize()

    if companion.agent_manager:
        # Generate a simple Python function
        result = await companion.agent_manager.generate_code(
            "Create a Python function that calculates the factorial of a number",
            "python",
        )

        if result.get("success"):
            print("Generated Code:")
            print(result["code"])
            print("\nExplanation:")
            print(result["explanation"])
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")

    await companion.stop()


async def demo_embedding():
    """Demo embedding functionality"""
    print("\n🔍 Demo: Text Embedding")
    print("-" * 40)

    companion = FusionAICompanion()
    await companion.initialize()

    if companion.embedding_service:
        # Embed some text
        text = (
            "This is a sample text about artificial intelligence and machine learning."
        )
        embedding = await companion.embedding_service.embed_text(text)

        print(f"Text: {text}")
        print(f"Embedding dimensions: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")

    await companion.stop()


async def demo_chat():
    """Demo chat functionality"""
    print("\n💬 Demo: AI Chat")
    print("-" * 40)

    companion = FusionAICompanion()
    await companion.initialize()

    if companion.agent_manager:
        # Simple chat
        response = await companion.agent_manager.chat(
            "Hello! Can you explain what you can help me with?"
        )

        print("User: Hello! Can you explain what you can help me with?")
        print(f"AI: {response}")

    await companion.stop()


async def run_quick_demos():
    """Run quick demonstrations of key features"""
    print("🚀 FusionAI Companion - Quick Demo")
    print("=" * 50)
    print("This script demonstrates core functionality.")
    print("Make sure Docker services are running first!")
    print("")

    try:
        # Run demos
        await demo_chat()
        await demo_code_generation()
        await demo_embedding()

        print("\n✅ Demo completed successfully!")
        print("\nNext steps:")
        print("1. Start the full application: python main.py")
        print("2. Open the web interface: http://localhost:8888")
        print("3. Explore the API documentation: http://localhost:8888/docs")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Docker services are running: docker-compose up -d")
        print("2. Check if all models are downloaded")
        print("3. Verify your .env configuration")


def main():
    """Main entry point"""
    try:
        asyncio.run(run_quick_demos())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
