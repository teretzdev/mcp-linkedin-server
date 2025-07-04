#!/usr/bin/env python3
"""
Deployment Configuration for LinkedIn Job Hunter
Addresses deployment and environment management gaps
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class DeploymentConfig:
    """Deployment configuration manager"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.config = self._load_config()
        self.base_path = Path(__file__).parent
    
    def _load_config(self) -> Dict[str, Any]:
        """Load deployment configuration"""
        config_file = f"deployment_config_{self.environment}.json"
        
        if Path(config_file).exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            "environment": self.environment,
            "services": {
                "api_bridge": {
                    "port": 8001,
                    "host": "localhost",
                    "workers": 1,
                    "timeout": 30
                },
                "mcp_backend": {
                    "port": 8002,
                    "host": "localhost",
                    "workers": 1,
                    "timeout": 30
                },
                "llm_controller": {
                    "port": 8003,
                    "host": "localhost",
                    "workers": 1,
                    "timeout": 30
                },
                "frontend": {
                    "port": 3000,
                    "host": "localhost",
                    "build_command": "npm run build",
                    "start_command": "npm start"
                }
            },
            "database": {
                "type": "sqlite",
                "path": "linkedin_jobs.db",
                "backup_enabled": True,
                "backup_interval": 3600  # 1 hour
            },
            "security": {
                "jwt_secret": os.getenv("JWT_SECRET_KEY", "change-in-production"),
                "cors_origins": ["http://localhost:3000"],
                "rate_limit_enabled": True,
                "ssl_enabled": False
            },
            "monitoring": {
                "logging_level": "INFO",
                "log_file": "app.log",
                "metrics_enabled": True,
                "health_check_interval": 60
            },
            "backup": {
                "enabled": True,
                "schedule": "0 */6 * * *",  # Every 6 hours
                "retention_days": 7,
                "backup_path": "backups/"
            }
        }
    
    def validate_environment(self) -> bool:
        """Validate deployment environment"""
        logger.info(f"Validating environment: {self.environment}")
        
        checks = [
            self._check_python_version(),
            self._check_dependencies(),
            self._check_node_installation(),
            self._check_database_connection(),
            self._check_ports_availability(),
            self._check_file_permissions()
        ]
        
        all_passed = all(checks)
        logger.info(f"Environment validation: {'✅ PASSED' if all_passed else '❌ FAILED'}")
        return all_passed
    
    def _check_python_version(self) -> bool:
        """Check Python version compatibility"""
        try:
            version = sys.version_info
            if version.major < 3 or (version.major == 3 and version.minor < 8):
                logger.error(f"Python 3.8+ required, found {version.major}.{version.minor}")
                return False
            logger.info(f"Python version: {version.major}.{version.minor}.{version.micro}")
            return True
        except Exception as e:
            logger.error(f"Error checking Python version: {e}")
            return False
    
    def _check_dependencies(self) -> bool:
        """Check Python dependencies"""
        try:
            import fastapi
            import uvicorn
            import playwright
            import psutil
            import jwt
            logger.info("All required Python dependencies found")
            return True
        except ImportError as e:
            logger.error(f"Missing dependency: {e}")
            return False
    
    def _check_node_installation(self) -> bool:
        """Check Node.js installation"""
        try:
            result = subprocess.run(["node", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info(f"Node.js version: {result.stdout.strip()}")
                return True
            else:
                logger.error("Node.js not found")
                return False
        except Exception as e:
            logger.error(f"Error checking Node.js: {e}")
            return False
    
    def _check_database_connection(self) -> bool:
        """Check database connection"""
        try:
            from database.database import Database
            db = Database()
            # Test connection
            logger.info("Database connection successful")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def _check_ports_availability(self) -> bool:
        """Check if required ports are available"""
        try:
            import socket
            
            for service_name, service_config in self.config["services"].items():
                if "port" in service_config:
                    port = service_config["port"]
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex(('localhost', port))
                    sock.close()
                    
                    if result == 0:
                        logger.warning(f"Port {port} is already in use")
                        return False
                    else:
                        logger.info(f"Port {port} is available")
            
            return True
        except Exception as e:
            logger.error(f"Error checking ports: {e}")
            return False
    
    def _check_file_permissions(self) -> bool:
        """Check file permissions"""
        try:
            # Check if we can write to the current directory
            test_file = self.base_path / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
            
            # Check if we can create logs directory
            logs_dir = self.base_path / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            logger.info("File permissions check passed")
            return True
        except Exception as e:
            logger.error(f"File permissions check failed: {e}")
            return False
    
    def setup_environment(self) -> bool:
        """Setup deployment environment"""
        logger.info("Setting up deployment environment...")
        
        try:
            # Create necessary directories
            self._create_directories()
            
            # Setup environment variables
            self._setup_env_vars()
            
            # Install dependencies
            self._install_dependencies()
            
            # Setup database
            self._setup_database()
            
            # Setup monitoring
            self._setup_monitoring()
            
            logger.info("Environment setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Environment setup failed: {e}")
            return False
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = [
            "logs",
            "backups",
            "sessions",
            "resumes",
            "test_reports",
            "test_screenshots"
        ]
        
        for directory in directories:
            dir_path = self.base_path / directory
            dir_path.mkdir(exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def _setup_env_vars(self):
        """Setup environment variables"""
        env_file = self.base_path / ".env"
        
        if not env_file.exists():
            env_content = f"""# LinkedIn Job Hunter Environment Configuration
ENVIRONMENT={self.environment}

# LinkedIn Credentials
LINKEDIN_USERNAME=your_email@example.com
LINKEDIN_PASSWORD=your_password

# API Keys
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

# Security
JWT_SECRET_KEY={self.config['security']['jwt_secret']}
COOKIE_ENCRYPTION_KEY=your_cookie_encryption_key

# Database
DATABASE_PATH={self.config['database']['path']}

# Monitoring
LOG_LEVEL={self.config['monitoring']['logging_level']}
LOG_FILE={self.config['monitoring']['log_file']}

# Development
DEBUG=true
HEADLESS=true
TIMEOUT=30000
"""
            env_file.write_text(env_content)
            logger.info("Created .env file")
    
    def _install_dependencies(self):
        """Install Python and Node.js dependencies"""
        try:
            # Install Python dependencies
            logger.info("Installing Python dependencies...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True, capture_output=True)
            
            # Install Node.js dependencies
            if (self.base_path / "package.json").exists():
                logger.info("Installing Node.js dependencies...")
                subprocess.run(["npm", "install"], check=True, capture_output=True)
            
            logger.info("Dependencies installed successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            raise
    
    def _setup_database(self):
        """Setup database"""
        try:
            from database.migrations import run_migrations
            run_migrations()
            logger.info("Database setup completed")
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            raise
    
    def _setup_monitoring(self):
        """Setup monitoring and logging"""
        try:
            # Configure logging
            log_config = {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "standard": {
                        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                    }
                },
                "handlers": {
                    "file": {
                        "class": "logging.FileHandler",
                        "filename": self.config["monitoring"]["log_file"],
                        "formatter": "standard"
                    },
                    "console": {
                        "class": "logging.StreamHandler",
                        "formatter": "standard"
                    }
                },
                "root": {
                    "handlers": ["file", "console"],
                    "level": self.config["monitoring"]["logging_level"]
                }
            }
            
            log_config_file = self.base_path / "logging_config.json"
            with open(log_config_file, 'w') as f:
                json.dump(log_config, f, indent=2)
            
            logger.info("Monitoring setup completed")
            
        except Exception as e:
            logger.error(f"Monitoring setup failed: {e}")
            raise
    
    def deploy(self) -> bool:
        """Deploy the application"""
        logger.info(f"Starting deployment for environment: {self.environment}")
        
        try:
            # Validate environment
            if not self.validate_environment():
                logger.error("Environment validation failed")
                return False
            
            # Setup environment
            if not self.setup_environment():
                logger.error("Environment setup failed")
                return False
            
            # Start services
            if not self._start_services():
                logger.error("Service startup failed")
                return False
            
            logger.info("Deployment completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return False
    
    def _start_services(self) -> bool:
        """Start application services"""
        try:
            # Start API Bridge
            logger.info("Starting API Bridge...")
            subprocess.Popen([
                sys.executable, "api_bridge.py"
            ], cwd=self.base_path)
            
            # Start MCP Backend
            logger.info("Starting MCP Backend...")
            subprocess.Popen([
                sys.executable, "linkedin_browser_mcp.py"
            ], cwd=self.base_path)
            
            # Start Frontend (if in development)
            if self.environment == "development":
                logger.info("Starting Frontend...")
                subprocess.Popen([
                    "npm", "start"
                ], cwd=self.base_path)
            
            logger.info("All services started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start services: {e}")
            return False
    
    def generate_deployment_script(self) -> str:
        """Generate deployment script"""
        script_content = f"""#!/bin/bash
# LinkedIn Job Hunter Deployment Script
# Environment: {self.environment}

set -e

echo "Starting deployment for {self.environment} environment..."

# Check Python version
python3 --version

# Install Python dependencies
pip3 install -r requirements.txt

# Install Node.js dependencies
npm install

# Run deployment
python3 deployment_config.py --deploy --environment {self.environment}

echo "Deployment completed successfully!"
"""
        
        script_file = self.base_path / f"deploy_{self.environment}.sh"
        script_file.write_text(script_content)
        script_file.chmod(0o755)
        
        logger.info(f"Deployment script generated: {script_file}")
        return str(script_file)

def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LinkedIn Job Hunter Deployment")
    parser.add_argument("--environment", default="development", 
                       choices=["development", "staging", "production"],
                       help="Deployment environment")
    parser.add_argument("--validate", action="store_true",
                       help="Validate environment only")
    parser.add_argument("--setup", action="store_true",
                       help="Setup environment only")
    parser.add_argument("--deploy", action="store_true",
                       help="Full deployment")
    parser.add_argument("--generate-script", action="store_true",
                       help="Generate deployment script")
    
    args = parser.parse_args()
    
    config = DeploymentConfig(args.environment)
    
    if args.validate:
        success = config.validate_environment()
        sys.exit(0 if success else 1)
    
    elif args.setup:
        success = config.setup_environment()
        sys.exit(0 if success else 1)
    
    elif args.deploy:
        success = config.deploy()
        sys.exit(0 if success else 1)
    
    elif args.generate_script:
        script_path = config.generate_deployment_script()
        print(f"Deployment script generated: {script_path}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 