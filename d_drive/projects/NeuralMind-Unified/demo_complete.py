#!/usr/bin/env python3
"""
FusionAI Companion Complete Demo
Comprehensive demonstration of all system capabilities
"""

import asyncio
import json
import sys
import time
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from main import FusionAICompanion


class FusionAIDemo:
    """Complete demonstration of FusionAI Companion capabilities"""

    def __init__(self):
        self.companion = None

    def print_section(self, title: str, description: str = ""):
        """Print a formatted section header"""
        print("\n" + "=" * 60)
        print(f"🚀 {title}")
        if description:
            print(f"   {description}")
        print("=" * 60)

    def print_subsection(self, title: str):
        """Print a formatted subsection header"""
        print(f"\n🔸 {title}")
        print("-" * 40)

    async def initialize_system(self):
        """Initialize the FusionAI Companion system"""
        self.print_section("System Initialization", "Starting all components")

        try:
            self.companion = FusionAICompanion()
            await self.companion.initialize()
            print("✅ All components initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False

    async def demo_agent_capabilities(self):
        """Demonstrate AI agent capabilities"""
        self.print_section("AI Agent Capabilities", "Code generation, review, and chat")

        if not self.companion.agent_manager:
            print("⚠️ Agent manager not available")
            return

        # Code Generation Demo
        self.print_subsection("Code Generation")
        try:
            result = await self.companion.agent_manager.generate_code(
                "Create a Python function that calculates fibonacci numbers recursively",
                "python",
            )

            if result.get("success"):
                print("Generated Code:")
                print("-" * 20)
                print(result["code"])
                print("-" * 20)
                print(f"Explanation: {result.get('explanation', 'N/A')}")
            else:
                print(f"❌ Code generation failed: {result.get('error')}")
        except Exception as e:
            print(f"❌ Code generation error: {e}")

        # Chat Demo
        self.print_subsection("AI Chat")
        try:
            questions = [
                "What programming languages do you support?",
                "Explain the benefits of async programming in Python",
                "How can you help with code review?",
            ]

            for question in questions:
                print(f"User: {question}")
                response = await self.companion.agent_manager.chat(question)
                print(f"AI: {response}")
                print()
        except Exception as e:
            print(f"❌ Chat demo error: {e}")

    async def demo_embedding_service(self):
        """Demonstrate embedding and RAG capabilities"""
        self.print_section(
            "Embedding & RAG Service", "Text processing and semantic search"
        )

        if not self.companion.embedding_service:
            print("⚠️ Embedding service not available")
            return

        # Text Embedding Demo
        self.print_subsection("Text Embedding")
        try:
            test_texts = [
                "Python is a high-level programming language",
                "Machine learning enables computers to learn from data",
                "FastAPI is a modern web framework for Python",
            ]

            for text in test_texts:
                embedding = await self.companion.embedding_service.embed_text(text)
                print(f"Text: {text[:50]}...")
                print(f"Embedding dimensions: {len(embedding)}")
                print(f"First 5 values: {embedding[:5]}")
                print()
        except Exception as e:
            print(f"❌ Embedding demo error: {e}")

        # Document Processing Demo
        self.print_subsection("Document Processing")
        try:
            # Simulate document processing
            sample_doc = """
            FusionAI Companion is a unified AI agent system that combines:
            1. Code generation and review capabilities
            2. VTuber avatar animation and streaming
            3. Workflow automation with n8n
            4. Semantic search and RAG functionality
            5. Web-based interface and REST API
            """

            result = await self.companion.embedding_service.process_document(
                sample_doc, {"title": "FusionAI Overview", "type": "documentation"}
            )

            if result.get("success"):
                print(f"✅ Processed document with {result.get('chunks', 0)} chunks")
            else:
                print(f"❌ Document processing failed")
        except Exception as e:
            print(f"❌ Document processing error: {e}")

    async def demo_vtuber_controller(self):
        """Demonstrate VTuber capabilities"""
        self.print_section("VTuber Controller", "Avatar animation and streaming")

        if not self.companion.avatar_controller:
            print("⚠️ VTuber controller not available (may be disabled)")
            return

        # Animation Demo
        self.print_subsection("Avatar Animation")
        try:
            # Test different expressions
            expressions = ["happy", "surprised", "thinking"]
            for expression in expressions:
                print(f"Setting expression: {expression}")
                await self.companion.avatar_controller.set_expression(expression)
                await asyncio.sleep(1)

            print("✅ Expression changes completed")
        except Exception as e:
            print(f"❌ Animation demo error: {e}")

        # Speech Demo
        self.print_subsection("Text-to-Speech")
        try:
            test_phrases = [
                "Hello! I am your FusionAI companion!",
                "I can help you with coding and much more!",
                "Let's build amazing things together!",
            ]

            for phrase in test_phrases:
                print(f"Speaking: {phrase}")
                await self.companion.avatar_controller.speak(phrase)
                await asyncio.sleep(2)

            print("✅ Speech demo completed")
        except Exception as e:
            print(f"❌ Speech demo error: {e}")

    async def demo_workflow_manager(self):
        """Demonstrate workflow automation"""
        self.print_section("Workflow Manager", "n8n automation and orchestration")

        if not self.companion.workflow_manager:
            print("⚠️ Workflow manager not available")
            return

        # Workflow Status Demo
        self.print_subsection("Workflow Status")
        try:
            status = await self.companion.workflow_manager.get_status()
            print(f"Workflow system status: {status.get('status', 'Unknown')}")
            print(f"Active workflows: {status.get('active_workflows', 0)}")
            print(f"n8n connection: {status.get('n8n_connected', False)}")
        except Exception as e:
            print(f"❌ Workflow status error: {e}")

        # Workflow Execution Demo
        self.print_subsection("Workflow Execution")
        try:
            # Example workflow execution (if available)
            test_data = {"message": "Test workflow execution", "timestamp": time.time()}

            result = await self.companion.workflow_manager.execute_workflow(
                "test_workflow", test_data
            )

            if result.get("success"):
                print("✅ Workflow executed successfully")
            else:
                print("ℹ️ No test workflow available (normal for new setup)")
        except Exception as e:
            print(f"❌ Workflow execution error: {e}")

    async def demo_api_endpoints(self):
        """Demonstrate web API functionality"""
        self.print_section("Web API", "REST endpoints and web interface")

        print("🌐 Available API endpoints:")
        endpoints = [
            "GET  /health - System health check",
            "POST /agent/chat - AI chat interface",
            "POST /agent/generate - Code generation",
            "POST /embedding/embed - Text embedding",
            "POST /embedding/search - Semantic search",
            "GET  /vtuber/status - VTuber status",
            "POST /vtuber/speak - Text-to-speech",
            "GET  /workflows/status - Workflow status",
            "GET  /docs - API documentation",
        ]

        for endpoint in endpoints:
            print(f"  • {endpoint}")

        print("\n🔗 Access points:")
        print("  • Web Interface: http://localhost:8888")
        print("  • API Documentation: http://localhost:8888/docs")
        print("  • Health Check: http://localhost:8888/health")

    async def run_system_health_check(self):
        """Run comprehensive system health check"""
        self.print_section("System Health Check", "Verifying all components")

        health_status = {}

        # Check each component
        components = [
            ("Agent Manager", self.companion.agent_manager),
            ("Embedding Service", self.companion.embedding_service),
            ("Avatar Controller", self.companion.avatar_controller),
            ("Workflow Manager", self.companion.workflow_manager),
        ]

        for name, component in components:
            if component and hasattr(component, "health_check"):
                try:
                    is_healthy = await component.health_check()
                    health_status[name] = is_healthy
                    status = "✅ Healthy" if is_healthy else "❌ Unhealthy"
                    print(f"  {status} - {name}")
                except Exception as e:
                    health_status[name] = False
                    print(f"  ❌ Error - {name}: {e}")
            elif component:
                health_status[name] = True
                print(f"  ✅ Available - {name}")
            else:
                health_status[name] = False
                print(f"  ⚠️ Disabled - {name}")

        # Overall health summary
        healthy_count = sum(health_status.values())
        total_count = len(health_status)

        print(f"\n📊 Overall Health: {healthy_count}/{total_count} components healthy")

        if healthy_count == total_count:
            print("🎉 All systems operational!")
        elif healthy_count > 0:
            print("⚠️ Partial functionality available")
        else:
            print("❌ System not operational")

    async def cleanup(self):
        """Clean up and shutdown"""
        self.print_section("Cleanup", "Shutting down system")

        if self.companion:
            await self.companion.stop()
            print("✅ System shutdown complete")

    async def run_complete_demo(self):
        """Run the complete demonstration"""
        print("🎬 FusionAI Companion - Complete Demo")
        print("This demo will showcase all system capabilities")
        print("\nPress Ctrl+C at any time to stop the demo")

        try:
            # Initialize system
            if not await self.initialize_system():
                return False

            # Run all demo sections
            await self.demo_agent_capabilities()
            await self.demo_embedding_service()
            await self.demo_vtuber_controller()
            await self.demo_workflow_manager()
            await self.demo_api_endpoints()
            await self.run_system_health_check()

            # Final summary
            self.print_section("Demo Complete", "All features demonstrated")
            print("🎉 Demo completed successfully!")
            print("\n📚 To learn more:")
            print("  • Read the documentation in docs/")
            print("  • Explore the API at http://localhost:8888/docs")
            print("  • Try the quickstart: python quickstart.py")
            print("  • Run health checks: python health_check.py")

            return True

        except KeyboardInterrupt:
            print("\n\n⚠️ Demo interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            return False
        finally:
            await self.cleanup()


async def main():
    """Main entry point"""
    demo = FusionAIDemo()

    try:
        success = await demo.run_complete_demo()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Demo error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
