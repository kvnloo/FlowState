"""Core Utilities Package.

This package provides reusable utility modules for the FlowState backend:

Modules:
    logger : Centralized logging configuration and structured logging
    validators : Comprehensive data validation for EEG, biometric, and user data

Example:
    >>> from core.utils.logger import get_logger
    >>> from core.utils.validators import validate_eeg_chunk
    >>>
    >>> logger = get_logger(__name__)
    >>> logger.info("Processing EEG data")
"""

from .logger import get_logger, setup_logging, log_context
from .validators import (
    ValidationError,
    validate_eeg_chunk,
    validate_channel_names,
    validate_heart_rate,
    validate_hrv,
    validate_temperature,
    validate_user_id,
    validate_email,
    validate_url,
    validate_port,
    validate_path,
    validate_timestamp,
    validate_dict_schema
)

__all__ = [
    # Logger
    'get_logger',
    'setup_logging',
    'log_context',
    # Validators
    'ValidationError',
    'validate_eeg_chunk',
    'validate_channel_names',
    'validate_heart_rate',
    'validate_hrv',
    'validate_temperature',
    'validate_user_id',
    'validate_email',
    'validate_url',
    'validate_port',
    'validate_path',
    'validate_timestamp',
    'validate_dict_schema'
]
