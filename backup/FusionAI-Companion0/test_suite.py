#!/usr/bin/env python3
"""
FusionAI Companion Test Suite
Basic tests to verify all components are working correctly
"""

import asyncio
import json
import sys
import time
from pathlib import Path

import httpx

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))


class FusionAITester:
    """Test suite for FusionAI Companion"""

    def __init__(self):
        self.base_url = "http://localhost:8888"
        self.test_results = []

    async def test_health_endpoint(self):
        """Test the health check endpoint"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/health")

                if response.status_code == 200:
                    data = response.json()
                    return {"test": "health_endpoint", "status": "pass", "data": data}
                else:
                    return {
                        "test": "health_endpoint",
                        "status": "fail",
                        "error": f"HTTP {response.status_code}",
                    }

        except Exception as e:
            return {"test": "health_endpoint", "status": "error", "error": str(e)}

    async def test_agent_chat(self):
        """Test the AI agent chat functionality"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/agent/chat",
                    json={
                        "message": "Hello! Can you tell me what 2+2 equals?",
                        "context": None,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    if "response" in data:
                        return {
                            "test": "agent_chat",
                            "status": "pass",
                            "response": (
                                data["response"][:100] + "..."
                                if len(data["response"]) > 100
                                else data["response"]
                            ),
                        }
                    else:
                        return {
                            "test": "agent_chat",
                            "status": "fail",
                            "error": "No response in data",
                        }
                else:
                    return {
                        "test": "agent_chat",
                        "status": "fail",
                        "error": f"HTTP {response.status_code}",
                    }

        except Exception as e:
            return {"test": "agent_chat", "status": "error", "error": str(e)}

    async def test_code_generation(self):
        """Test code generation functionality"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/agent/generate-code",
                    json={
                        "prompt": "Create a simple hello world function in Python",
                        "language": "python",
                        "context": None,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "code" in data:
                        return {
                            "test": "code_generation",
                            "status": "pass",
                            "code_preview": (
                                data["code"][:100] + "..."
                                if len(data["code"]) > 100
                                else data["code"]
                            ),
                        }
                    else:
                        return {
                            "test": "code_generation",
                            "status": "fail",
                            "error": data.get("error", "Unknown error"),
                        }
                else:
                    return {
                        "test": "code_generation",
                        "status": "fail",
                        "error": f"HTTP {response.status_code}",
                    }

        except Exception as e:
            return {"test": "code_generation", "status": "error", "error": str(e)}

    async def test_embedding_service(self):
        """Test text embedding functionality"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/embed/text",
                    json={"text": "This is a test sentence for embedding."},
                )

                if response.status_code == 200:
                    data = response.json()
                    if "embedding" in data and len(data["embedding"]) > 0:
                        return {
                            "test": "embedding_service",
                            "status": "pass",
                            "embedding_size": len(data["embedding"]),
                        }
                    else:
                        return {
                            "test": "embedding_service",
                            "status": "fail",
                            "error": "No embedding in response",
                        }
                else:
                    return {
                        "test": "embedding_service",
                        "status": "fail",
                        "error": f"HTTP {response.status_code}",
                    }

        except Exception as e:
            return {"test": "embedding_service", "status": "error", "error": str(e)}

    async def test_workflows_list(self):
        """Test workflow listing functionality"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/workflows")

                if response.status_code == 200:
                    data = response.json()
                    if "workflows" in data:
                        return {
                            "test": "workflows_list",
                            "status": "pass",
                            "workflow_count": len(data["workflows"]),
                        }
                    else:
                        return {
                            "test": "workflows_list",
                            "status": "fail",
                            "error": "No workflows in response",
                        }
                else:
                    return {
                        "test": "workflows_list",
                        "status": "fail",
                        "error": f"HTTP {response.status_code}",
                    }

        except Exception as e:
            return {"test": "workflows_list", "status": "error", "error": str(e)}

    async def run_all_tests(self):
        """Run all tests and return results"""
        print("🧪 Running FusionAI Companion Tests")
        print("=" * 40)

        tests = [
            ("Health Check", self.test_health_endpoint()),
            ("Agent Chat", self.test_agent_chat()),
            ("Code Generation", self.test_code_generation()),
            ("Embedding Service", self.test_embedding_service()),
            ("Workflows List", self.test_workflows_list()),
        ]

        results = []

        for test_name, test_coro in tests:
            print(f"Running {test_name}...", end=" ")

            try:
                result = await test_coro
                results.append(result)

                status = result["status"]
                if status == "pass":
                    print("✅ PASS")
                elif status == "fail":
                    print(f"❌ FAIL - {result.get('error', 'Unknown error')}")
                else:
                    print(f"⚠️ ERROR - {result.get('error', 'Unknown error')}")

            except Exception as e:
                print(f"💥 EXCEPTION - {e}")
                results.append(
                    {
                        "test": test_name.lower().replace(" ", "_"),
                        "status": "exception",
                        "error": str(e),
                    }
                )

        return results

    def print_summary(self, results):
        """Print test summary"""
        total_tests = len(results)
        passed_tests = len([r for r in results if r["status"] == "pass"])
        failed_tests = len(
            [r for r in results if r["status"] in ["fail", "error", "exception"]]
        )

        print("\n📊 Test Summary")
        print("=" * 40)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")

        if failed_tests > 0:
            print("\n🔍 Failed Tests:")
            for result in results:
                if result["status"] != "pass":
                    test_name = result["test"].replace("_", " ").title()
                    error = result.get("error", "Unknown error")
                    print(f"  • {test_name}: {error}")

        print("\n💡 Tips:")
        print("  • Make sure all Docker services are running: docker-compose up -d")
        print("  • Wait 30-60 seconds for services to fully initialize")
        print("  • Check health status: python health_check.py")
        print("  • View logs: docker-compose logs -f")


async def main():
    """Main entry point"""
    tester = FusionAITester()

    try:
        print("Waiting for services to be ready...")
        await asyncio.sleep(5)  # Give services time to start

        results = await tester.run_all_tests()
        tester.print_summary(results)

        # Save results
        output_file = Path("logs/test_results.json")
        output_file.parent.mkdir(exist_ok=True)

        test_report = {
            "timestamp": time.time(),
            "results": results,
            "summary": {
                "total": len(results),
                "passed": len([r for r in results if r["status"] == "pass"]),
                "failed": len([r for r in results if r["status"] != "pass"]),
            },
        }

        with open(output_file, "w") as f:
            json.dump(test_report, f, indent=2)

        print(f"\n📝 Test results saved to: {output_file}")

        # Exit with appropriate code
        failed_tests = len([r for r in results if r["status"] != "pass"])
        sys.exit(0 if failed_tests == 0 else 1)

    except KeyboardInterrupt:
        print("\n❌ Tests interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
