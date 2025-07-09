import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_config() -> dict:
    """
    Loads the main server configuration from mcp_config.json.

    This function locates the configuration file relative to the project's
    root directory, loads it, and returns it as a dictionary.

    Returns:
        A dictionary containing the server configuration.
    
    Raises:
        FileNotFoundError: If the config file cannot be found.
        json.JSONDecodeError: If the config file is not valid JSON.
    """
    try:
        # The project root is two levels up from this file's parent directory
        # (core -> mcp_server -> enhanced-mcp-server)
        project_root = Path(__file__).resolve().parent.parent.parent
        config_path = project_root / 'config' / 'mcp_config.json'
        
        logger.info(f"Attempting to load configuration from: {config_path}")
        
        if not config_path.exists():
            logger.error(f"Configuration file not found at {config_path}")
            raise FileNotFoundError(f"Configuration file not found at {config_path}")

        with open(config_path, 'r') as f:
            config = json.load(f)
            logger.info("Configuration loaded successfully.")
            return config
            
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from config file: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading config: {e}")
        raise 