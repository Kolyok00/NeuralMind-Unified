#!/usr/bin/env python3
"""
FusionAI Companion Health Check Utility
Checks the status of all services and components
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import httpx

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))


class HealthChecker:
    """Health check utility for FusionAI Companion"""

    def __init__(self):
        self.services = {
            "Ollama": {"url": "http://localhost:11434", "endpoint": "/api/tags"},
            "Open WebUI": {"url": "http://localhost:3000", "endpoint": "/health"},
            "n8n": {"url": "http://localhost:5678", "endpoint": "/healthz"},
            "Langfuse": {
                "url": "http://localhost:3001",
                "endpoint": "/api/public/health",
            },
            "Neo4j": {"url": "http://localhost:7474", "endpoint": "/"},
            "SearXNG": {"url": "http://localhost:8080", "endpoint": "/"},
            "Crawl4AI": {"url": "http://localhost:8000", "endpoint": "/health"},
            "Whisper": {"url": "http://localhost:8081", "endpoint": "/"},
            "FusionAI API": {"url": "http://localhost:8888", "endpoint": "/health"},
        }

        self.docker_services = [
            "fusionai-ollama",
            "fusionai-open-webui",
            "fusionai-n8n",
            "fusionai-langfuse",
            "fusionai-neo4j",
            "fusionai-searxng",
            "fusionai-crawl4ai",
            "fusionai-whisper",
            "fusionai-supabase-db",
            "fusionai-redis",
        ]

    async def check_service_http(
        self, name: str, url: str, endpoint: str = "/"
    ) -> Dict[str, Any]:
        """Check if an HTTP service is responding"""
        full_url = f"{url}{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(full_url)
                return {
                    "name": name,
                    "status": "healthy" if response.status_code < 500 else "unhealthy",
                    "url": url,
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code,
                }
        except httpx.ConnectError:
            return {
                "name": name,
                "status": "unreachable",
                "url": url,
                "error": "Connection refused",
            }
        except httpx.TimeoutException:
            return {
                "name": name,
                "status": "timeout",
                "url": url,
                "error": "Request timeout",
            }
        except Exception as e:
            return {"name": name, "status": "error", "url": url, "error": str(e)}

    async def check_docker_container(self, container_name: str) -> Dict[str, Any]:
        """Check if a Docker container is running"""
        try:
            import subprocess

            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    f"name={container_name}",
                    "--format",
                    "{{.Names}}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and container_name in result.stdout:
                # Get container status
                status_result = subprocess.run(
                    [
                        "docker",
                        "inspect",
                        container_name,
                        "--format",
                        "{{.State.Status}}",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                status = (
                    status_result.stdout.strip()
                    if status_result.returncode == 0
                    else "unknown"
                )

                return {
                    "name": container_name,
                    "status": "running" if status == "running" else status,
                    "type": "docker_container",
                }
            else:
                return {
                    "name": container_name,
                    "status": "not_found",
                    "type": "docker_container",
                }

        except subprocess.TimeoutExpired:
            return {
                "name": container_name,
                "status": "timeout",
                "type": "docker_container",
                "error": "Docker command timeout",
            }
        except FileNotFoundError:
            return {
                "name": container_name,
                "status": "docker_not_found",
                "type": "docker_container",
                "error": "Docker command not found",
            }
        except Exception as e:
            return {
                "name": container_name,
                "status": "error",
                "type": "docker_container",
                "error": str(e),
            }

    async def check_all_services(self) -> Dict[str, Any]:
        """Check all services and return comprehensive status"""
        print("🔍 Checking FusionAI Companion Health...")
        print("=" * 50)

        # Check HTTP services
        http_tasks = []
        for name, config in self.services.items():
            task = self.check_service_http(
                name, config["url"], config.get("endpoint", "/")
            )
            http_tasks.append(task)

        print("Checking HTTP services...")
        http_results = await asyncio.gather(*http_tasks, return_exceptions=True)

        # Check Docker containers
        print("Checking Docker containers...")
        docker_tasks = []
        for container in self.docker_services:
            task = self.check_docker_container(container)
            docker_tasks.append(task)

        docker_results = await asyncio.gather(*docker_tasks, return_exceptions=True)

        # Process results
        healthy_services = 0
        total_services = len(http_results) + len(docker_results)

        all_results = {
            "timestamp": time.time(),
            "http_services": [],
            "docker_containers": [],
            "summary": {},
        }

        # Process HTTP results
        for result in http_results:
            if isinstance(result, Exception):
                all_results["http_services"].append(
                    {"name": "unknown", "status": "error", "error": str(result)}
                )
            else:
                all_results["http_services"].append(result)
                if result.get("status") == "healthy":
                    healthy_services += 1

        # Process Docker results
        for result in docker_results:
            if isinstance(result, Exception):
                all_results["docker_containers"].append(
                    {"name": "unknown", "status": "error", "error": str(result)}
                )
            else:
                all_results["docker_containers"].append(result)
                if result.get("status") == "running":
                    healthy_services += 1

        # Generate summary
        all_results["summary"] = {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "health_percentage": (
                (healthy_services / total_services * 100) if total_services > 0 else 0
            ),
            "overall_status": (
                "healthy" if healthy_services >= total_services * 0.8 else "degraded"
            ),
        }

        return all_results

    def print_results(self, results: Dict[str, Any]):
        """Print health check results in a readable format"""
        print("\n📊 Health Check Results")
        print("=" * 50)

        # Print summary
        summary = results["summary"]
        status_emoji = "✅" if summary["overall_status"] == "healthy" else "⚠️"
        print(f"{status_emoji} Overall Status: {summary['overall_status'].upper()}")
        print(
            f"📈 Health: {summary['healthy_services']}/{summary['total_services']} services ({summary['health_percentage']:.1f}%)"
        )
        print()

        # Print HTTP services
        print("🌐 HTTP Services:")
        for service in results["http_services"]:
            status = service.get("status", "unknown")
            emoji = (
                "✅"
                if status == "healthy"
                else "❌" if status in ["error", "unhealthy"] else "⚠️"
            )
            name = service.get("name", "Unknown")

            if "response_time" in service:
                print(f"  {emoji} {name}: {status} ({service['response_time']:.2f}s)")
            else:
                error = service.get("error", "Unknown error")
                print(f"  {emoji} {name}: {status} - {error}")

        print()

        # Print Docker containers
        print("🐳 Docker Containers:")
        for container in results["docker_containers"]:
            status = container.get("status", "unknown")
            emoji = "✅" if status == "running" else "❌" if status == "error" else "⚠️"
            name = container.get("name", "Unknown")

            if "error" in container:
                print(f"  {emoji} {name}: {status} - {container['error']}")
            else:
                print(f"  {emoji} {name}: {status}")

        print()

        # Print recommendations
        if summary["overall_status"] != "healthy":
            print("🔧 Recommendations:")

            unhealthy_http = [
                s for s in results["http_services"] if s.get("status") != "healthy"
            ]
            unhealthy_docker = [
                s for s in results["docker_containers"] if s.get("status") != "running"
            ]

            if unhealthy_docker:
                print("  • Start Docker services: docker-compose up -d")

            if unhealthy_http:
                print("  • Wait for services to initialize (may take 30-60 seconds)")
                print("  • Check Docker logs: docker-compose logs -f")

            print("  • Verify .env configuration")
            print("  • Ensure no port conflicts")


async def main():
    """Main entry point"""
    checker = HealthChecker()

    try:
        results = await checker.check_all_services()
        checker.print_results(results)

        # Save results to file
        output_file = Path("logs/health_check.json")
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"📝 Detailed results saved to: {output_file}")

        # Exit with appropriate code
        overall_status = results["summary"]["overall_status"]
        sys.exit(0 if overall_status == "healthy" else 1)

    except KeyboardInterrupt:
        print("\n❌ Health check interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Health check failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
