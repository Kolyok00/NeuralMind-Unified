#!/usr/bin/env python3
"""
FusionAI Companion Demo Script
Simple demonstration of core functionality
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))


async def demo_core_features():
    """Demo core FusionAI features"""

    try:
        from main import FusionAICompanion

        print("🚀 FusionAI Companion Demo")
        print("=" * 40)

        # Initialize system
        print("\n📦 Initializing system...")
        companion = FusionAICompanion()
        await companion.initialize()
        print("✅ System initialized!")

        # Demo Agent
        print("\n🤖 Testing AI Agent...")
        if companion.agent_manager:
            response = await companion.agent_manager.chat(
                "Hello! What can you help me with?"
            )
            print(f"AI: {response}")
        else:
            print("⚠️ Agent not available")

        # Demo Embedding
        print("\n🔍 Testing Embedding Service...")
        if companion.embedding_service:
            text = "This is a test for embedding"
            embedding = await companion.embedding_service.embed_text(text)
            print(f"Embedded text with {len(embedding)} dimensions")
        else:
            print("⚠️ Embedding service not available")

        # Demo VTuber (if enabled)
        print("\n🎭 Testing VTuber Controller...")
        if companion.avatar_controller:
            print("VTuber controller is available!")
        else:
            print("ℹ️ VTuber controller disabled (normal)")

        # Demo Workflows
        print("\n🔄 Testing Workflow Manager...")
        if companion.workflow_manager:
            active = companion.workflow_manager.get_active_workflows()
            print(f"Active workflows: {len(active)}")
        else:
            print("⚠️ Workflow manager not available")

        # Web API info
        print("\n🌐 Web API Information:")
        print("  • Interface: http://localhost:8888")
        print("  • API Docs: http://localhost:8888/docs")
        print("  • Health: http://localhost:8888/health")

        # Cleanup
        print("\n🧹 Cleaning up...")
        await companion.stop()
        print("✅ Demo completed successfully!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

    return True


async def main():
    """Main entry point"""
    print("Starting FusionAI Companion Demo...")

    try:
        success = await demo_core_features()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
