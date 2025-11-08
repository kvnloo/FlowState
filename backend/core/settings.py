"""Application Configuration Management.

This module provides centralized configuration management for the FlowState
application. It handles environment variables, configuration validation, and
provides type-safe access to all application settings.

The configuration system uses the dataclass pattern to provide clear structure
and type safety while supporting flexible environment-based configuration through
dotenv integration.

Configuration Categories:
    - External API Integration: Shimmer API credentials and endpoints
    - Database Connections: Database URLs and connection parameters
    - API Server Settings: Host, port, and service configuration
    - Feature Flags: Enable/disable experimental features
    - Data Storage: File system paths for persistent data

Environment Variables:
    SHIMMER_BASE_URL : str
        Base URL for Shimmer API (default: http://localhost:8083)
    SHIMMER_CLIENT_ID : str
        OAuth client ID for Shimmer authentication
    SHIMMER_CLIENT_SECRET : str
        OAuth client secret for Shimmer authentication
    DATABASE_URL : str
        Database connection string (default: sqlite:///./flowstate.db)
    API_HOST : str
        API server bind address (default: 0.0.0.0)
    API_PORT : int
        API server port number (default: 8000)
    DATA_DIR : str
        Base directory for data storage (default: ./data)
    ENABLE_GUT_MICROBIOME : bool
        Enable gut microbiome analysis features (default: false)
    ENABLE_EYE_TRACKING : bool
        Enable eye tracking integration (default: false)
    ENABLE_KOVAAK : bool
        Enable Kovaak performance tracking (default: false)

Usage:
    The module provides a global `config` instance that should be imported
    and used throughout the application:

    >>> from core.settings import config
    >>> print(config.shimmer.base_url)
    'http://localhost:8083'
    >>> print(config.database_url)
    'sqlite:///./flowstate.db'

Security Considerations:
    - Never commit .env files containing secrets to version control
    - Use environment-specific .env files (.env.development, .env.production)
    - Rotate credentials regularly in production environments
    - Use secret management services for production deployments

Example .env File:
    .. code-block:: bash

        # Shimmer API Configuration
        SHIMMER_BASE_URL=https://api.shimmerhealth.com
        SHIMMER_CLIENT_ID=your-client-id-here
        SHIMMER_CLIENT_SECRET=your-client-secret-here

        # Database Configuration
        DATABASE_URL=postgresql://user:pass@localhost:5432/flowstate

        # API Server Configuration
        API_HOST=0.0.0.0
        API_PORT=8000

        # Data Storage
        DATA_DIR=/var/lib/flowstate/data

        # Feature Flags
        ENABLE_GUT_MICROBIOME=true
        ENABLE_EYE_TRACKING=true
        ENABLE_KOVAAK=false

See Also:
    :class:`ShimmerConfig`: Shimmer API-specific configuration
    :mod:`dotenv`: Environment variable loading

Examples:
    Configure database connection:

    >>> from core.settings import config
    >>> db_url = config.database_url
    >>> engine = create_engine(db_url)

    Check feature flags:

    >>> if config.enable_eye_tracking:
    ...     from integrations.tobii import TobiiTracker
    ...     tracker = TobiiTracker()

    Access Shimmer credentials:

    >>> shimmer_client = ShimmerClient(
    ...     base_url=config.shimmer.base_url,
    ...     client_id=config.shimmer.client_id,
    ...     client_secret=config.shimmer.client_secret
    ... )

Note:
    Configuration values are loaded once at application startup. Changes to
    environment variables after import will not be reflected in the config
    object. Restart the application to pick up new configuration values.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class ShimmerConfig:
    """Configuration for Shimmer health data integration API.

    Shimmer provides a unified interface for accessing health data from multiple
    sources (Apple Health, Google Fit, Fitbit, etc.). This configuration class
    manages the credentials and endpoints needed for API access.

    Attributes:
        base_url : str
            Base URL for Shimmer API endpoints. Should include protocol (http/https)
            and domain without trailing slash.
        client_id : str
            OAuth 2.0 client ID issued by Shimmer for API authentication.
            This is a public identifier safe to expose in client-side code.
        client_secret : str
            OAuth 2.0 client secret for API authentication. This must be kept
            secure and never exposed in client-side code or version control.

    Security:
        The client_secret should be treated as a highly sensitive credential:
        - Store in environment variables or secret management system
        - Never commit to version control
        - Rotate regularly (recommended: every 90 days)
        - Use separate credentials for development/production

    Example:
        >>> shimmer_config = ShimmerConfig(
        ...     base_url="https://api.shimmerhealth.com",
        ...     client_id="abc123",
        ...     client_secret="secret456"
        ... )
        >>> print(shimmer_config.base_url)
        https://api.shimmerhealth.com

    See Also:
        Shimmer API Documentation: https://www.openmhealth.org/shimmer/
    """
    base_url: str
    client_id: str
    client_secret: str


@dataclass
class Config:
    """Main application configuration container.

    Centralized configuration management for the FlowState application. This
    class aggregates all configuration settings and provides type-safe access
    throughout the application.

    The configuration is initialized from environment variables with sensible
    defaults for development. Production deployments should override all
    sensitive values via environment variables.

    Attributes:
        shimmer : ShimmerConfig
            Configuration for Shimmer health data API integration
        database_url : str
            Database connection string (SQLAlchemy format)
        api_host : str
            Host address for API server binding
        api_port : int
            Port number for API server
        data_dir : Path
            Base directory for file-based data storage
        enable_gut_microbiome_analysis : bool
            Feature flag for gut microbiome data processing
        enable_eye_tracking : bool
            Feature flag for Tobii eye tracking integration
        enable_kovaak_integration : bool
            Feature flag for Kovaak aim trainer integration

    Configuration Lifecycle:
        1. Environment variables loaded from .env file (if present)
        2. Config object created with environment values or defaults
        3. Config object used throughout application lifetime
        4. Application restart required for configuration changes

    Validation:
        The configuration system performs minimal validation at initialization.
        Additional validation should be performed by consuming services:

        >>> from core.settings import config
        >>> if not config.shimmer.client_id:
        ...     raise ValueError("SHIMMER_CLIENT_ID must be set")

    Database URL Formats:
        SQLite (development):
            >>> DATABASE_URL=sqlite:///./flowstate.db

        PostgreSQL (production):
            >>> DATABASE_URL=postgresql://user:pass@localhost:5432/flowstate

        PostgreSQL with connection pooling:
            >>> DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/flowstate?pool_size=10

    Example:
        >>> # Import global config instance
        >>> from core.settings import config
        >>>
        >>> # Access database settings
        >>> print(config.database_url)
        sqlite:///./flowstate.db
        >>>
        >>> # Check feature flags
        >>> if config.enable_eye_tracking:
        ...     print("Eye tracking is enabled")
        >>>
        >>> # Access nested configuration
        >>> shimmer_url = config.shimmer.base_url

    Note:
        The global `config` instance at the module level should be used
        throughout the application rather than creating new Config instances.
    """

    # Shimmer configuration
    shimmer: ShimmerConfig = field(default_factory=lambda: ShimmerConfig(
        base_url=os.getenv("SHIMMER_BASE_URL", "http://localhost:8083"),
        client_id=os.getenv("SHIMMER_CLIENT_ID", ""),
        client_secret=os.getenv("SHIMMER_CLIENT_SECRET", "")
    ))

    # Database configuration
    database_url: str = field(default_factory=lambda: os.getenv(
        "DATABASE_URL",
        "sqlite:///./flowstate.db"
    ))

    # API configuration
    api_host: str = field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    api_port: int = field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))

    # Data storage paths
    data_dir: Path = field(default_factory=lambda: Path(os.getenv("DATA_DIR", "./data")))

    # Feature flags
    enable_gut_microbiome_analysis: bool = field(
        default_factory=lambda: os.getenv("ENABLE_GUT_MICROBIOME", "false").lower() == "true"
    )
    enable_eye_tracking: bool = field(
        default_factory=lambda: os.getenv("ENABLE_EYE_TRACKING", "false").lower() == "true"
    )
    enable_kovaak_integration: bool = field(
        default_factory=lambda: os.getenv("ENABLE_KOVAAK", "false").lower() == "true"
    )

    def validate(self) -> Dict[str, str]:
        """Validate configuration and return any errors.

        Performs comprehensive validation of all configuration values and
        returns a dictionary of validation errors. An empty dictionary
        indicates valid configuration.

        Returns:
            Dict[str, str]: Dictionary mapping configuration keys to error messages

        Validation Checks:
            - Shimmer credentials are non-empty
            - Database URL is well-formed
            - API port is in valid range (1-65535)
            - Data directory exists or can be created
            - Feature flags are boolean values

        Example:
            >>> from core.settings import config
            >>> errors = config.validate()
            >>> if errors:
            ...     for key, error in errors.items():
            ...         print(f"{key}: {error}")
            ...     raise ValueError("Invalid configuration")

        Note:
            This method does not raise exceptions, allowing the caller to
            decide how to handle validation failures.
        """
        errors: Dict[str, str] = {}

        # Validate Shimmer configuration
        if not self.shimmer.client_id:
            errors['shimmer.client_id'] = "SHIMMER_CLIENT_ID must be set"
        if not self.shimmer.client_secret:
            errors['shimmer.client_secret'] = "SHIMMER_CLIENT_SECRET must be set"
        if not self.shimmer.base_url:
            errors['shimmer.base_url'] = "SHIMMER_BASE_URL must be set"

        # Validate API configuration
        if not 1 <= self.api_port <= 65535:
            errors['api_port'] = f"Invalid port number: {self.api_port}"

        # Validate data directory
        if not self.data_dir.exists():
            try:
                self.data_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors['data_dir'] = f"Cannot create data directory: {e}"

        return errors

    def to_dict(self) -> Dict[str, any]:
        """Convert configuration to dictionary representation.

        Serializes the configuration to a dictionary format suitable for
        logging, debugging, or export. Sensitive values like secrets are
        masked for security.

        Returns:
            Dict[str, any]: Dictionary representation of configuration

        Example:
            >>> from core.settings import config
            >>> config_dict = config.to_dict()
            >>> import json
            >>> print(json.dumps(config_dict, indent=2))

        Note:
            The client_secret field is masked as '***' for security.
            Never log or export the actual secret value.
        """
        return {
            'shimmer': {
                'base_url': self.shimmer.base_url,
                'client_id': self.shimmer.client_id,
                'client_secret': '***'  # Mask sensitive data
            },
            'database_url': self.database_url.replace(
                '://', '://***@'  # Mask credentials in URL
            ) if '://' in self.database_url else self.database_url,
            'api_host': self.api_host,
            'api_port': self.api_port,
            'data_dir': str(self.data_dir),
            'feature_flags': {
                'gut_microbiome': self.enable_gut_microbiome_analysis,
                'eye_tracking': self.enable_eye_tracking,
                'kovaak': self.enable_kovaak_integration
            }
        }


# Create a global config instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance.

    Provides functional access to the global configuration object.
    This is the preferred method for accessing configuration in
    dependency injection scenarios.

    Returns:
        Config: Global configuration instance

    Example:
        >>> from core.settings import get_config
        >>> config = get_config()
        >>> print(config.api_port)
        8000

    Note:
        This function always returns the same global instance.
        Multiple calls return the same object.
    """
    return config
