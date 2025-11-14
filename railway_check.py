"""
Railway Deployment Readiness Check
Validates that the application is ready for Railway deployment
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def check_requirements_file():
    """Check if requirements.txt exists"""
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("❌ requirements.txt not found!")
        return False
    print("✅ requirements.txt found")
    return True


def check_dockerfile():
    """Check if Dockerfile exists"""
    dockerfile = Path("Dockerfile")
    if not dockerfile.exists():
        print("❌ Dockerfile not found!")
        return False
    print("✅ Dockerfile found")
    return True


def check_env_not_committed():
    """Warn if .env file exists (shouldn't be in git)"""
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file found - make sure it's in .gitignore!")
        return True
    print("✅ No .env file (good - use Railway variables)")
    return True


def check_essential_files():
    """Check if essential application files exist"""
    essential = ["main.py", "config/settings.py", "agents/base_agent.py"]
    all_good = True

    for file in essential:
        path = Path(file)
        if not path.exists():
            print(f"❌ Essential file missing: {file}")
            all_good = False
        else:
            print(f"✅ {file} found")

    return all_good


def check_port_configuration():
    """Check if main.py uses PORT env variable"""
    main_file = Path("main.py")

    if not main_file.exists():
        return False

    content = main_file.read_text(encoding='utf-8')

    # Check if it reads PORT from environment
    if "os.getenv" in content or "settings.API_PORT" in content:
        print("✅ Port configuration looks good")
        return True
    else:
        print("⚠️  Make sure your app uses $PORT environment variable")
        return True


def check_dependencies():
    """Check if critical dependencies are in requirements.txt"""
    req_file = Path("requirements.txt")

    if not req_file.exists():
        return False

    content = req_file.read_text()
    critical_deps = ["fastapi", "uvicorn", "pydantic", "aiohttp"]

    missing = []
    for dep in critical_deps:
        if dep not in content.lower():
            missing.append(dep)

    if missing:
        print(f"⚠️  Possibly missing dependencies: {', '.join(missing)}")
    else:
        print("✅ Critical dependencies found")

    return True


def main():
    """Run all checks"""
    print("=" * 60)
    print("🚂 RAILWAY DEPLOYMENT READINESS CHECK")
    print("=" * 60)
    print()

    checks = [
        ("Requirements file", check_requirements_file),
        ("Dockerfile", check_dockerfile),
        ("Environment file", check_env_not_committed),
        ("Essential files", check_essential_files),
        ("Port configuration", check_port_configuration),
        ("Dependencies", check_dependencies),
    ]

    results = []

    for name, check_func in checks:
        print(f"\n🔍 Checking: {name}")
        print("-" * 60)
        result = check_func()
        results.append(result)
        print()

    print("=" * 60)

    if all(results):
        print("✅ ALL CHECKS PASSED!")
        print("🚀 Your application is ready for Railway deployment!")
        print()
        print("Next steps:")
        print("1. Push your code to GitHub")
        print("2. Create new project on Railway.app")
        print("3. Connect your GitHub repository")
        print("4. Set Root Directory to 'backend'")
        print("5. Configure environment variables")
        print("6. Deploy!")
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("Please fix the issues above before deploying")
        return 1


if __name__ == "__main__":
    sys.exit(main())
