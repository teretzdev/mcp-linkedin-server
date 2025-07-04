#!/usr/bin/env python3
"""
Health Check Script for Enhanced MCP Server
Checks the health and status of the MCP server components with new directory structure
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Add the enhanced server to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set shared paths
shared_root = project_root.parent / 'shared'

def check_file_permissions():
    """Check if required directories and files have proper permissions"""
    issues = []
    
    # Check shared sessions directory
    sessions_dir = shared_root / "sessions"
    if not sessions_dir.exists():
        issues.append("Shared sessions directory does not exist")
    elif not os.access(sessions_dir, os.W_OK):
        issues.append("Shared sessions directory is not writable")
    
    # Check shared logs directory
    logs_dir = shared_root / "logs"
    if not logs_dir.exists():
        issues.append("Shared logs directory does not exist")
    elif not os.access(logs_dir, os.W_OK):
        issues.append("Shared logs directory is not writable")
    
    # Check shared database file
    db_file = shared_root / "database" / "linkedin_jobs.db"
    if db_file.exists() and not os.access(db_file, os.R_OK | os.W_OK):
        issues.append("Shared database file is not accessible")
    
    return issues

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        "fastmcp",
        "playwright",
        "cryptography",
        "sqlalchemy",
        "pydantic",
        "structlog"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def check_configuration():
    """Check if configuration files exist and are valid"""
    issues = []
    
    # Check main config file
    config_file = project_root / "config" / "mcp_config.json"
    if not config_file.exists():
        issues.append("Enhanced server configuration file does not exist")
    else:
        try:
            with open(config_file, 'r') as f:
                json.load(f)
        except json.JSONDecodeError:
            issues.append("Enhanced server configuration file is not valid JSON")
    
    # Check legacy config file
    legacy_config_file = project_root.parent / "legacy" / "config.json"
    if not legacy_config_file.exists():
        issues.append("Legacy server configuration file does not exist")
    else:
        try:
            with open(legacy_config_file, 'r') as f:
                json.load(f)
        except json.JSONDecodeError:
            issues.append("Legacy server configuration file is not valid JSON")
    
    return issues

def check_browser_installation():
    """Check if Playwright browsers are installed"""
    try:
        from playwright.async_api import async_playwright
        return []
    except ImportError:
        return ["Playwright is not installed"]
    
    # Note: This would require a browser context to fully test
    # For now, we'll just check if the package is available

def check_directory_structure():
    """Check if the new directory structure is properly set up"""
    issues = []
    
    # Check enhanced server structure
    enhanced_server = project_root
    if not enhanced_server.exists():
        issues.append("Enhanced server directory does not exist")
    else:
        required_dirs = ["mcp_server", "config", "scripts"]
        for dir_name in required_dirs:
            dir_path = enhanced_server / dir_name
            if not dir_path.exists():
                issues.append(f"Enhanced server {dir_name} directory does not exist")
    
    # Check legacy server structure
    legacy_server = project_root.parent / "legacy"
    if not legacy_server.exists():
        issues.append("Legacy server directory does not exist")
    else:
        required_files = ["linkedin_browser_mcp.py", "api_bridge.py", "mcp_client.py"]
        for file_name in required_files:
            file_path = legacy_server / file_name
            if not file_path.exists():
                issues.append(f"Legacy server {file_name} does not exist")
    
    # Check shared structure
    if not shared_root.exists():
        issues.append("Shared directory does not exist")
    else:
        required_shared_dirs = ["database", "sessions", "logs", "config"]
        for dir_name in required_shared_dirs:
            dir_path = shared_root / dir_name
            if not dir_path.exists():
                issues.append(f"Shared {dir_name} directory does not exist")
    
    return issues

async def check_server_status():
    """Check if the MCP server is running and responding"""
    # This would typically check if the server is listening on the expected port
    # For now, we'll return a basic status
    return {
        "status": "unknown",
        "message": "Server status check not implemented in this version"
    }

def main():
    """Main health check function"""
    print("🔍 LinkedIn Job Hunter Enhanced MCP Server Health Check")
    print("=" * 60)
    
    all_issues = []
    
    # Check directory structure
    print("\n📁 Checking directory structure...")
    structure_issues = check_directory_structure()
    if structure_issues:
        all_issues.extend(structure_issues)
        for issue in structure_issues:
            print(f"  ❌ {issue}")
    else:
        print("  ✅ Directory structure is correct")
    
    # Check file permissions
    print("\n📁 Checking file permissions...")
    permission_issues = check_file_permissions()
    if permission_issues:
        all_issues.extend(permission_issues)
        for issue in permission_issues:
            print(f"  ❌ {issue}")
    else:
        print("  ✅ File permissions are correct")
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    missing_packages = check_dependencies()
    if missing_packages:
        all_issues.extend([f"Missing package: {pkg}" for pkg in missing_packages])
        for pkg in missing_packages:
            print(f"  ❌ Missing package: {pkg}")
    else:
        print("  ✅ All required packages are installed")
    
    # Check configuration
    print("\n⚙️  Checking configuration...")
    config_issues = check_configuration()
    if config_issues:
        all_issues.extend(config_issues)
        for issue in config_issues:
            print(f"  ❌ {issue}")
    else:
        print("  ✅ Configuration is valid")
    
    # Check browser installation
    print("\n🌐 Checking browser installation...")
    browser_issues = check_browser_installation()
    if browser_issues:
        all_issues.extend(browser_issues)
        for issue in browser_issues:
            print(f"  ❌ {issue}")
    else:
        print("  ✅ Browser automation is available")
    
    # Check server status
    print("\n🖥️  Checking server status...")
    try:
        server_status = asyncio.run(check_server_status())
        print(f"  ℹ️  {server_status['message']}")
    except Exception as e:
        print(f"  ❌ Server status check failed: {e}")
        all_issues.append(f"Server status check failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Health Check Summary")
    print("=" * 60)
    
    if all_issues:
        print(f"❌ Found {len(all_issues)} issues:")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")
        print("\n💡 Recommendations:")
        print("  - Install missing packages: pip install -r enhanced-mcp-server/requirements.txt")
        print("  - Check file permissions and create missing directories")
        print("  - Verify configuration files are valid JSON")
        print("  - Ensure Playwright browsers are installed: playwright install")
        print("  - Run the refactoring script to fix directory structure")
        return 1
    else:
        print("✅ All health checks passed!")
        print("🎉 The enhanced MCP server should be ready to run.")
        print(f"📁 Enhanced server: {project_root}")
        print(f"📁 Legacy server: {project_root.parent / 'legacy'}")
        print(f"📁 Shared resources: {shared_root}")
        return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Health check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during health check: {e}")
        sys.exit(1) 