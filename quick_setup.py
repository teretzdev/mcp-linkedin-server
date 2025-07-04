#!/usr/bin/env python3
"""
Quick Setup Script for LinkedIn Job Hunter
Helps users set up the environment and dependencies quickly
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    print("=" * 60)
    print("🚀 LinkedIn Job Hunter - Quick Setup")
    print("=" * 60)

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✅ Python dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install Python dependencies: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Timeout installing Python dependencies")
        return False

def check_node_installation():
    """Check if Node.js is installed"""
    print("\n🟢 Checking Node.js installation...")
    try:
        # Check Node.js
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("❌ Node.js not found")
            print("📥 Please install Node.js from: https://nodejs.org/")
            return False
        
        # Check npm
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("❌ npm not found")
            return False
        
        print("✅ Node.js and npm are installed")
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Node.js not found")
        print("📥 Please install Node.js from: https://nodejs.org/")
        return False

def install_npm_dependencies():
    """Install npm dependencies"""
    print("\n📦 Installing npm dependencies...")
    try:
        result = subprocess.run(['npm', 'install'], capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✅ npm dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install npm dependencies: {result.stderr}")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Failed to run npm install")
        return False

def setup_environment():
    """Setup environment file"""
    print("\n⚙️ Setting up environment...")
    
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    try:
        # Run the create_env.py script
        result = subprocess.run([sys.executable, 'create_env.py'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Environment file created successfully")
            print("📝 Please edit .env file with your credentials")
            return True
        else:
            print(f"❌ Failed to create environment file: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Timeout creating environment file")
        return False

def install_playwright_browsers():
    """Install Playwright browsers"""
    print("\n🌐 Installing Playwright browsers...")
    try:
        result = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✅ Playwright browsers installed successfully")
            return True
        else:
            print(f"❌ Failed to install Playwright browsers: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Timeout installing Playwright browsers")
        return False

def create_startup_script():
    """Create a simple startup script"""
    print("\n🚀 Creating startup script...")
    
    if platform.system() == "Windows":
        script_content = """@echo off
echo Starting LinkedIn Job Hunter...
python auto_startup.py
pause
"""
        script_file = "start.bat"
    else:
        script_content = """#!/bin/bash
echo "Starting LinkedIn Job Hunter..."
python3 auto_startup.py
"""
        script_file = "start.sh"
    
    try:
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        if platform.system() != "Windows":
            os.chmod(script_file, 0o755)
        
        print(f"✅ Startup script created: {script_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to create startup script: {e}")
        return False

def main():
    """Main setup function"""
    print_header()
    
    checks = [
        ("Python Version", check_python_version),
        ("Python Dependencies", install_python_dependencies),
        ("Node.js Installation", check_node_installation),
        ("npm Dependencies", install_npm_dependencies),
        ("Environment Setup", setup_environment),
        ("Playwright Browsers", install_playwright_browsers),
        ("Startup Script", create_startup_script)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} failed with error: {e}")
            results.append((check_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 SETUP SUMMARY")
    print("=" * 60)
    
    passed = 0
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:<25} {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"Results: {passed}/{len(results)} checks passed")
    
    if passed == len(results):
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file with your LinkedIn credentials")
        print("2. Run: python auto_startup.py")
        print("3. Or use the created startup script")
    else:
        print("\n⚠️ Some checks failed. Please fix the issues above and run again.")
        print("\nCommon solutions:")
        print("- Install Node.js from https://nodejs.org/")
        print("- Make sure you have internet connection")
        print("- Run as administrator if needed")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 