#!/usr/bin/env python3
"""
FusionAI Companion Project Validator
Comprehensive validation of project setup and dependencies
"""

import json
import sys
from pathlib import Path
from typing import Dict


class ProjectValidator:
    """Validates FusionAI Companion project setup"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results = {}

    def print_header(self):
        """Print validation header"""
        print("=" * 60)
        print("         FusionAI Companion Project Validator")
        print("=" * 60)

    def check_python_version(self) -> bool:
        """Check Python version"""
        version = sys.version_info
        required = (3, 8)

        if version >= required:
            print(f"✅ Python {version.major}.{version.minor} (OK)")
            return True
        else:
            print(f"❌ Python {version.major}.{version.minor} (Need 3.8+)")
            return False

    def check_dependencies(self) -> bool:
        """Check key dependencies"""
        print("\n📦 Checking Dependencies:")

        dependencies = ["fastapi", "uvicorn", "pydantic", "httpx", "aiohttp"]

        missing = []
        for dep in dependencies:
            try:
                __import__(dep)
                print(f"  ✅ {dep}")
            except ImportError:
                print(f"  ❌ {dep}")
                missing.append(dep)

        if missing:
            print(f"\n⚠️ Missing dependencies: {', '.join(missing)}")
            print("Run: pip install -r requirements.txt")
            return False

        return True

    def check_project_structure(self) -> bool:
        """Check project directory structure"""
        print("\n📁 Checking Project Structure:")

        required_dirs = [
            "core_agent",
            "ingest",
            "vtuber",
            "workflows",
            "config",
            "static",
            "logs",
        ]

        required_files = [
            "main.py",
            "web_server.py",
            "requirements.txt",
            "README.md",
            "config/main.json",
            ".env.example",
        ]

        missing_dirs = []
        for directory in required_dirs:
            dir_path = self.project_root / directory
            if dir_path.exists():
                print(f"  📁 ✅ {directory}/")
            else:
                print(f"  📁 ❌ {directory}/")
                missing_dirs.append(directory)

        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"  📄 ✅ {file_path}")
            else:
                print(f"  📄 ❌ {file_path}")
                missing_files.append(file_path)

        return len(missing_dirs) == 0 and len(missing_files) == 0

    def check_configuration(self) -> bool:
        """Check configuration files"""
        print("\n⚙️ Checking Configuration:")

        config_file = self.project_root / "config" / "main.json"
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"

        # Check main config
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)

                required_sections = [
                    "core_agent",
                    "embedding",
                    "vtuber",
                    "workflows",
                    "web_ui",
                ]

                for section in required_sections:
                    if section in config:
                        print(f"  ✅ Config section: {section}")
                    else:
                        print(f"  ❌ Missing config: {section}")

            except json.JSONDecodeError:
                print("  ❌ Invalid JSON in config/main.json")
                return False
        else:
            print("  ❌ config/main.json not found")
            return False

        # Check env files
        if env_example.exists():
            print("  ✅ .env.example exists")
        else:
            print("  ❌ .env.example missing")

        if env_file.exists():
            print("  ✅ .env file exists")
        else:
            print("  ⚠️ .env file not found (copy from .env.example)")

        return True

    def check_core_modules(self) -> bool:
        """Check core module imports"""
        print("\n🧩 Checking Core Modules:")

        modules = [
            ("core_agent.agent_manager", "AgentManager"),
            ("ingest.embedding_service", "EmbeddingService"),
            ("vtuber.avatar_controller", "AvatarController"),
            ("workflows.workflow_manager", "WorkflowManager"),
            ("web_server", "FusionAIWebServer"),
        ]

        # Add project to path
        sys.path.insert(0, str(self.project_root))

        all_good = True
        for module_name, class_name in modules:
            try:
                module = __import__(module_name, fromlist=[class_name])
                getattr(module, class_name)
                print(f"  ✅ {module_name}.{class_name}")
            except ImportError as e:
                print(f"  ❌ {module_name}: {e}")
                all_good = False
            except AttributeError:
                print(f"  ❌ {module_name}: {class_name} not found")
                all_good = False

        return all_good

    def check_utility_scripts(self) -> bool:
        """Check utility scripts"""
        print("\n🛠️ Checking Utility Scripts:")

        scripts = [
            "setup_simple.py",
            "quickstart.py",
            "demo_simple.py",
            "health_check.py",
            "test_suite.py",
        ]

        missing_scripts = []
        for script in scripts:
            script_path = self.project_root / script
            if script_path.exists():
                print(f"  ✅ {script}")
            else:
                print(f"  ❌ {script}")
                missing_scripts.append(script)

        return len(missing_scripts) == 0

    def check_static_files(self) -> bool:
        """Check static web files"""
        print("\n🌐 Checking Static Files:")

        static_files = ["static/index.html"]

        for file_path in static_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"  ✅ {file_path}")
            else:
                print(f"  ❌ {file_path}")
                return False

        return True

    def generate_report(self) -> Dict[str, bool]:
        """Generate comprehensive validation report"""
        self.print_header()

        # Run all checks
        checks = [
            ("Python Version", self.check_python_version),
            ("Dependencies", self.check_dependencies),
            ("Project Structure", self.check_project_structure),
            ("Configuration", self.check_configuration),
            ("Core Modules", self.check_core_modules),
            ("Utility Scripts", self.check_utility_scripts),
            ("Static Files", self.check_static_files),
        ]

        results = {}
        for check_name, check_func in checks:
            try:
                results[check_name] = check_func()
            except Exception as e:
                print(f"  ❌ {check_name}: Error - {e}")
                results[check_name] = False

        # Summary
        print("\n" + "=" * 60)
        print("                    VALIDATION SUMMARY")
        print("=" * 60)

        passed = sum(results.values())
        total = len(results)

        for check_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {check_name}")

        print("-" * 60)
        print(f"OVERALL: {passed}/{total} checks passed")

        if passed == total:
            print("🎉 PROJECT VALIDATION SUCCESSFUL!")
            print("\nNext steps:")
            print("1. Run: python main.py")
            print("2. Visit: http://localhost:8888")
            print("3. Try: python demo_simple.py")
        else:
            print("⚠️ SOME CHECKS FAILED")
            print("\nPlease fix the issues above before proceeding.")

        return results


def main():
    """Main validation entry point"""
    validator = ProjectValidator()
    results = validator.generate_report()

    # Exit with error code if validation failed
    if not all(results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
