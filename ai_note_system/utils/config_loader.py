"""
Configuration loader module for AI Note System.
Loads and validates configuration from YAML files.
Supports environment-specific configuration (development, testing, production).
"""

import os
import yaml
from pathlib import Path
import logging

# Create a simple logger for this module to avoid circular imports
logger = logging.getLogger("ai_note_system.config_loader")

# Define valid environments
VALID_ENVIRONMENTS = ["development", "testing", "production"]
DEFAULT_ENVIRONMENT = "development"

class ConfigLoader:
    """
    Configuration loader class for AI Note System.
    Handles loading and validating configuration from YAML files.
    Supports environment-specific configuration.
    """
    
    def __init__(self, config_path=None, environment=None):
        """
        Initialize the ConfigLoader.
        
        Args:
            config_path (str, optional): Path to the configuration file.
                If None, will look for config.yaml in the default location.
            environment (str, optional): Environment to load configuration for.
                If None, will use the PANSOPHY_ENV environment variable or default to 'development'.
        """
        self.config = {}
        self.config_path = config_path
        
        # Determine the environment
        if environment is None:
            environment = os.environ.get("PANSOPHY_ENV", DEFAULT_ENVIRONMENT)
        
        if environment not in VALID_ENVIRONMENTS:
            logger.warning(f"Invalid environment: {environment}. Using {DEFAULT_ENVIRONMENT} instead.")
            environment = DEFAULT_ENVIRONMENT
        
        self.environment = environment
        logger.info(f"Using environment: {self.environment}")
        
        if not self.config_path:
            # Default config path is in the config directory
            config_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "config"
            )
            
            # Try to load environment-specific config first
            env_config_path = os.path.join(config_dir, f"config.{self.environment}.yaml")
            if os.path.exists(env_config_path):
                self.config_path = env_config_path
            else:
                # Fall back to default config
                self.config_path = os.path.join(config_dir, "config.yaml")
                logger.warning(f"Environment-specific config not found: {env_config_path}. Using default config.")
    
    def load_config(self):
        """
        Load configuration from the YAML file.
        If using an environment-specific config, it will first load the default config
        and then override it with the environment-specific values.
        
        Returns:
            dict: The loaded configuration
        
        Raises:
            FileNotFoundError: If the configuration file is not found
            yaml.YAMLError: If the configuration file is not valid YAML
        """
        logger.info(f"Loading configuration for environment: {self.environment}")
        
        # First, try to load the default configuration
        default_config = {}
        default_config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config",
            "config.yaml"
        )
        
        if os.path.exists(default_config_path) and self.config_path != default_config_path:
            try:
                with open(default_config_path, 'r') as config_file:
                    default_config = yaml.safe_load(config_file)
                logger.debug(f"Default configuration loaded from {default_config_path}")
            except (FileNotFoundError, yaml.YAMLError) as e:
                logger.warning(f"Error loading default configuration: {e}")
        
        # Now load the environment-specific configuration
        logger.info(f"Loading configuration from {self.config_path}")
        
        try:
            with open(self.config_path, 'r') as config_file:
                env_config = yaml.safe_load(config_file)
                
            # Merge configurations: environment-specific config overrides default config
            if default_config:
                self.config = self._merge_configs(default_config, env_config)
            else:
                self.config = env_config
                
            logger.debug(f"Configuration loaded successfully")
            return self.config
            
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
            
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            raise
            
    def _merge_configs(self, default_config, override_config):
        """
        Merge two configurations, with override_config taking precedence.
        
        Args:
            default_config (dict): The default configuration
            override_config (dict): The configuration to override with
            
        Returns:
            dict: The merged configuration
        """
        merged_config = default_config.copy()
        
        for key, value in override_config.items():
            # If both configs have the same key and both values are dicts, merge them recursively
            if key in merged_config and isinstance(merged_config[key], dict) and isinstance(value, dict):
                merged_config[key] = self._merge_configs(merged_config[key], value)
            else:
                # Otherwise, override the value
                merged_config[key] = value
                
        return merged_config
    
    def validate_config(self):
        """
        Validate the loaded configuration.
        Includes environment-specific validation.
        
        Returns:
            bool: True if the configuration is valid, False otherwise
        """
        logger.info(f"Validating configuration for environment: {self.environment}")
        
        # Check if config is loaded
        if not self.config:
            logger.error("No configuration loaded")
            return False
        
        # Common required configuration keys for all environments
        required_keys = [
            "OPENAI_API_KEY",
            "LLM_MODEL",
            "EMBEDDING_MODEL",
            "DATABASE_TYPE"
        ]
        
        # Environment-specific required keys
        env_required_keys = {
            "development": [
                "DEVELOPMENT_MODE",
                "RELOAD_ON_CHANGE"
            ],
            "testing": [
                "TESTING_MODE",
                "USE_MOCK_DATA"
            ],
            "production": [
                "PRODUCTION_MODE",
                "ERROR_REPORTING"
            ]
        }
        
        # Add environment-specific required keys
        if self.environment in env_required_keys:
            required_keys.extend(env_required_keys[self.environment])
        
        # Check for required keys
        missing_keys = [key for key in required_keys if key not in self.config]
        
        if missing_keys:
            logger.error(f"Missing required configuration keys for {self.environment}: {missing_keys}")
            return False
        
        # Validate specific configuration values
        if self.config.get("DATABASE_TYPE") not in ["json", "sqlite"]:
            logger.error(f"Invalid DATABASE_TYPE: {self.config.get('DATABASE_TYPE')}")
            return False
        
        # Environment-specific validation
        if self.environment == "development":
            # Development-specific validation
            if not isinstance(self.config.get("DEVELOPMENT_MODE"), bool):
                logger.error("DEVELOPMENT_MODE must be a boolean")
                return False
                
        elif self.environment == "testing":
            # Testing-specific validation
            if not isinstance(self.config.get("TESTING_MODE"), bool):
                logger.error("TESTING_MODE must be a boolean")
                return False
                
        elif self.environment == "production":
            # Production-specific validation
            if not isinstance(self.config.get("PRODUCTION_MODE"), bool):
                logger.error("PRODUCTION_MODE must be a boolean")
                return False
            
            # In production, we should have rate limiting enabled
            if not self.config.get("RATE_LIMITING", False):
                logger.warning("RATE_LIMITING is not enabled in production")
        
        logger.debug(f"Configuration validation successful for environment: {self.environment}")
        return True
    
    def get_config(self):
        """
        Get the loaded configuration.
        
        Returns:
            dict: The loaded configuration
        """
        return self.config
    
    def get_value(self, key, default=None):
        """
        Get a specific configuration value.
        
        Args:
            key (str): The configuration key
            default: The default value to return if the key is not found
            
        Returns:
            The configuration value for the key, or the default value if not found
        """
        return self.config.get(key, default)


def load_config(config_path=None, environment=None):
    """
    Load configuration from the YAML file.
    
    Args:
        config_path (str, optional): Path to the configuration file.
            If None, will look for config.yaml in the default location.
        environment (str, optional): Environment to load configuration for.
            If None, will use the PANSOPHY_ENV environment variable or default to 'development'.
            
    Returns:
        dict: The loaded configuration
    """
    config_loader = ConfigLoader(config_path, environment)
    config = config_loader.load_config()
    
    if not config_loader.validate_config():
        logger.warning(f"Configuration validation failed for environment: {config_loader.environment}, using loaded config anyway")
    
    return config