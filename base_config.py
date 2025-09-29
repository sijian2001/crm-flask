"""
Base configuration management module

This module provides a base configuration class that can be extended by
specific configuration classes (CustomerConfig, ProductConfig, etc.) to
provide common functionality and ensure consistency across the application.
"""
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union


class BaseConfig(ABC):
    """
    Abstract base class for configuration management

    Provides common configuration functionality including:
    - Environment variable loading
    - Flask app integration
    - Configuration caching
    - Type-safe value retrieval
    """

    # Class-level cache for configuration instances
    _instances: Dict[str, 'BaseConfig'] = {}
    _flask_app: Optional[Any] = None

    def __init__(self):
        """Initialize base configuration"""
        self._config_cache: Optional[Dict[str, Any]] = None
        self._initialized = False

    @classmethod
    def get_instance(cls) -> 'BaseConfig':
        """
        Get singleton instance of configuration class

        Returns:
            Singleton instance of the configuration class
        """
        class_name = cls.__name__
        if class_name not in cls._instances:
            cls._instances[class_name] = cls()
        return cls._instances[class_name]

    @abstractmethod
    def get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration values

        Returns:
            Dictionary containing default configuration values
        """
        pass

    @abstractmethod
    def get_config_prefix(self) -> str:
        """
        Get configuration prefix for environment variables

        Returns:
            Prefix string (e.g., 'CUSTOMER_', 'PRODUCT_')
        """
        pass

    def get_config(self) -> Dict[str, Any]:
        """
        Get complete configuration with caching

        Returns:
            Dictionary containing all configuration settings
        """
        if self._config_cache is None:
            self._config_cache = self._load_config()
        return self._config_cache

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from all sources

        Returns:
            Dictionary containing loaded configuration
        """
        config = self.get_default_config().copy()

        # Load from environment variables
        self._update_from_env(config)

        # Load from Flask config if available
        if self._flask_app:
            self._update_from_flask_config(config)

        return config

    def _update_from_env(self, config: Dict[str, Any]) -> None:
        """
        Update configuration from environment variables

        Args:
            config: Configuration dictionary to update
        """
        prefix = self.get_config_prefix()

        # Generic environment variable loading
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                config_value = self._parse_env_value(value)
                self._set_nested_config(config, config_key, config_value)

    def _update_from_flask_config(self, config: Dict[str, Any]) -> None:
        """
        Update configuration from Flask app config

        Args:
            config: Configuration dictionary to update
        """
        if not self._flask_app:
            return

        flask_config = self._flask_app.config
        prefix = self.get_config_prefix()

        # Load Flask configuration values
        for key, value in flask_config.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                self._set_nested_config(config, config_key, value)

    def _parse_env_value(self, value: str) -> Union[str, int, float, bool]:
        """
        Parse environment variable value to appropriate type

        Args:
            value: String value from environment variable

        Returns:
            Parsed value with appropriate type
        """
        # Boolean values
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'

        # Integer values
        try:
            return int(value)
        except ValueError:
            pass

        # Float values
        try:
            return float(value)
        except ValueError:
            pass

        # String values (default)
        return value

    def _set_nested_config(self, config: Dict[str, Any], key: str, value: Any) -> None:
        """
        Set nested configuration value using dot notation

        Args:
            config: Configuration dictionary
            key: Key in dot notation (e.g., 'pagination.per_page')
            value: Value to set
        """
        keys = key.split('.')
        current = config

        # Navigate to the nested dictionary
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        # Set the final value
        current[keys[-1]] = value

    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with dot notation support

        Args:
            key: Configuration key in dot notation
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        config = self.get_config()
        keys = key.split('.')
        current = config

        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return default

    def set_value(self, key: str, value: Any) -> None:
        """
        Set configuration value with dot notation support

        Args:
            key: Configuration key in dot notation
            value: Value to set
        """
        config = self.get_config()
        self._set_nested_config(config, key, value)

    @classmethod
    def init_app(cls, app: Any) -> None:
        """
        Initialize configuration with Flask app

        Args:
            app: Flask application instance
        """
        cls._flask_app = app

        # Clear all cached configurations to reload with Flask config
        for instance in cls._instances.values():
            instance._config_cache = None
            instance._initialized = True

    def reload_config(self) -> None:
        """Reload configuration from all sources"""
        self._config_cache = None

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached configurations"""
        for instance in cls._instances.values():
            instance._config_cache = None

    def is_initialized(self) -> bool:
        """
        Check if configuration has been initialized with Flask app

        Returns:
            True if initialized with Flask app
        """
        return self._initialized

    def validate_config(self) -> Dict[str, str]:
        """
        Validate configuration values

        Returns:
            Dictionary of validation errors (empty if valid)
        """
        errors = {}
        config = self.get_config()

        # Basic validation - can be overridden by subclasses
        if not isinstance(config, dict):
            errors['config'] = 'Configuration must be a dictionary'

        return errors

    def get_summary(self) -> Dict[str, Any]:
        """
        Get configuration summary for debugging

        Returns:
            Dictionary containing configuration summary
        """
        return {
            'class': self.__class__.__name__,
            'initialized': self.is_initialized(),
            'config_prefix': self.get_config_prefix(),
            'config_keys': list(self.get_config().keys()) if self._config_cache else [],
            'flask_app_available': self._flask_app is not None
        }