"""
Centralized configuration management for the LinkedIn automation system.
"""
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = "sqlite:///linkedin_jobs.db"
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    cleanup_days: int = 30


@dataclass
class LinkedInCredentialsConfig:
    """LinkedIn credentials configuration"""
    username: str = ""
    password: str = ""
    
    @classmethod
    def from_env(cls) -> 'LinkedInCredentialsConfig':
        """Load from environment variables"""
        # Try both LINKEDIN_USERNAME and LINKEDIN_EMAIL for backwards compatibility
        username = os.getenv('LINKEDIN_USERNAME') or os.getenv('LINKEDIN_EMAIL', '')
        password = os.getenv('LINKEDIN_PASSWORD', '')
        
        return cls(
            username=username,
            password=password
        )


@dataclass
class AutomationSettings:
    """Automation behavior settings"""
    max_applications_per_cycle: int = 20
    cycle_delay_minutes: int = 30
    job_search_timeout_seconds: int = 300
    application_timeout_seconds: int = 120
    retry_attempts: int = 3
    retry_delay_seconds: int = 10


@dataclass
class APIConfig:
    """API server configuration"""
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = False
    cors_enabled: bool = True
    request_timeout_seconds: int = 300


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    log_dir: str = "logs"
    max_file_size_mb: int = 10
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class ServicePorts:
    """Service port configuration"""
    api_bridge: int = 8001
    job_management_api: int = 8003
    frontend: int = 3000
    mcp_backend: int = 8101
    llm_controller: int = 8201
    
    @classmethod
    def load_from_file(cls, file_path: str = "service_ports.json") -> 'ServicePorts':
        """Load service ports from file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return cls(
                api_bridge=data.get('api_bridge', 8001),
                job_management_api=data.get('job_management_api', 8003),
                frontend=data.get('frontend_port', 3000),
                mcp_backend=data.get('mcp_backend', 8101),
                llm_controller=data.get('llm_controller', 8201)
            )
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.warning(f"Could not load service ports from {file_path}: {e}")
            return cls()
    
    def save_to_file(self, file_path: str = "service_ports.json") -> None:
        """Save service ports to file"""
        data = {
            'api_bridge': self.api_bridge,
            'job_management_api': self.job_management_api,
            'frontend_port': self.frontend,
            'frontend_url': f"http://localhost:{self.frontend}",
            'mcp_backend': self.mcp_backend,
            'llm_controller': self.llm_controller,
            'started_at': str(datetime.now())
        }
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)


@dataclass
class RedisConfig:
    """Redis configuration"""
    host: str = os.getenv('REDIS_HOST', 'localhost')
    port: int = int(os.getenv('REDIS_PORT', '6379'))
    db: int = int(os.getenv('REDIS_DB', '0'))
    password: str = os.getenv('REDIS_PASSWORD', '')
    username: str = os.getenv('REDIS_USERNAME', '')
    url: str = os.getenv('REDIS_URL', '')


@dataclass
class AutomationConfig:
    """Master configuration class"""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    linkedin_credentials: LinkedInCredentialsConfig = field(default_factory=LinkedInCredentialsConfig)
    automation: AutomationSettings = field(default_factory=AutomationSettings)
    api: APIConfig = field(default_factory=APIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    service_ports: ServicePorts = field(default_factory=ServicePorts)
    redis: RedisConfig = field(default_factory=RedisConfig)
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # RabbitMQ helper properties for backward compatibility
    @property
    def rabbitmq_host(self) -> str:
        return self.rabbitmq.host
    
    @property
    def rabbitmq_port(self) -> int:
        return self.rabbitmq.port
    
    @property
    def rabbitmq_username(self) -> str:
        return self.rabbitmq.username
    
    @property
    def rabbitmq_password(self) -> str:
        return self.rabbitmq.password
    
    @property
    def rabbitmq_virtual_host(self) -> str:
        return self.rabbitmq.virtual_host
    
    @classmethod
    def load(cls, config_file: Optional[str] = None) -> 'AutomationConfig':
        """Load configuration from file and environment"""
        config = cls()
        
        # Load from file if provided
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                config = cls._from_dict(data)
            except Exception as e:
                logging.warning(f"Could not load config from {config_file}: {e}")
        
        # Override with environment variables
        config._load_from_env()
        
        # Load service ports from separate file
        config.service_ports = ServicePorts.load_from_file()
        
        return config
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables"""
        # Database
        if db_url := os.getenv('DATABASE_URL'):
            self.database.url = db_url
            
        # LinkedIn credentials
        self.linkedin_credentials = LinkedInCredentialsConfig.from_env()
        
        # RabbitMQ
        self.rabbitmq = RabbitMQConfig.from_env()
        
        # API
        if api_host := os.getenv('API_HOST'):
            self.api.host = api_host
        if api_port := os.getenv('API_PORT'):
            self.api.port = int(api_port)
            
        # Environment
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.debug = os.getenv('DEBUG', 'true').lower() == 'true'
        
        # Logging
        self.logging.level = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> 'AutomationConfig':
        """Create configuration from dictionary"""
        config = cls()
        
        # Update nested configurations
        if 'database' in data:
            db_data = data['database']
            config.database = DatabaseConfig(**db_data)
            
        if 'automation' in data:
            auto_data = data['automation']
            config.automation = AutomationSettings(**auto_data)
            
        if 'api' in data:
            api_data = data['api']
            config.api = APIConfig(**api_data)
            
        if 'logging' in data:
            log_data = data['logging']
            config.logging = LoggingConfig(**log_data)
            
        if 'rabbitmq' in data:
            rmq_data = data['rabbitmq']
            config.rabbitmq = RabbitMQConfig(**rmq_data)
            
        # Update top-level fields
        config.environment = data.get('environment', config.environment)
        config.debug = data.get('debug', config.debug)
        
        return config
    
    def save(self, config_file: str) -> None:
        """Save configuration to file"""
        data = {
            'database': {
                'url': self.database.url,
                'backup_enabled': self.database.backup_enabled,
                'backup_interval_hours': self.database.backup_interval_hours,
                'cleanup_days': self.database.cleanup_days
            },
            'automation': {
                'max_applications_per_cycle': self.automation.max_applications_per_cycle,
                'cycle_delay_minutes': self.automation.cycle_delay_minutes,
                'job_search_timeout_seconds': self.automation.job_search_timeout_seconds,
                'application_timeout_seconds': self.automation.application_timeout_seconds,
                'retry_attempts': self.automation.retry_attempts,
                'retry_delay_seconds': self.automation.retry_delay_seconds
            },
            'api': {
                'host': self.api.host,
                'port': self.api.port,
                'debug': self.api.debug,
                'cors_enabled': self.api.cors_enabled,
                'request_timeout_seconds': self.api.request_timeout_seconds
            },
            'logging': {
                'level': self.logging.level,
                'log_dir': self.logging.log_dir,
                'max_file_size_mb': self.logging.max_file_size_mb,
                'backup_count': self.logging.backup_count,
                'format': self.logging.format
            },
            'rabbitmq': {
                'host': self.rabbitmq.host,
                'port': self.rabbitmq.port,
                'username': self.rabbitmq.username,
                'password': self.rabbitmq.password,
                'virtual_host': self.rabbitmq.virtual_host,
                'connection_timeout': self.rabbitmq.connection_timeout,
                'heartbeat': self.rabbitmq.heartbeat,
                'retry_attempts': self.rabbitmq.retry_attempts,
                'retry_delay': self.rabbitmq.retry_delay
            },
            'environment': self.environment,
            'debug': self.debug
        }
        
        with open(config_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Validate LinkedIn credentials
        if not self.linkedin_credentials.username:
            errors.append("LinkedIn username is required")
        if not self.linkedin_credentials.password:
            errors.append("LinkedIn password is required")
            
        # Validate ports
        if not (1024 <= self.api.port <= 65535):
            errors.append(f"API port {self.api.port} is not in valid range (1024-65535)")
            
        # Validate timeouts
        if self.automation.job_search_timeout_seconds <= 0:
            errors.append("Job search timeout must be positive")
        if self.automation.application_timeout_seconds <= 0:
            errors.append("Application timeout must be positive")
            
        return errors


# Global configuration instance
_config: Optional[AutomationConfig] = None


def get_config() -> AutomationConfig:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = AutomationConfig.load()
    return _config


def reload_config(config_file: Optional[str] = None) -> AutomationConfig:
    """Reload configuration from file"""
    global _config
    _config = AutomationConfig.load(config_file)
    return _config 