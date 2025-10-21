import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime


class TechTestFormatter(logging.Formatter):
    """Custom formatter for techtest application"""
    
    def format(self, record):
        # Add custom fields
        record.timestamp = datetime.utcnow().isoformat()
        
        # Color coding for console output
        colors = {
            'DEBUG': '\033[36m',    # Cyan
            'INFO': '\033[32m',     # Green  
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',    # Red
            'CRITICAL': '\033[35m', # Magenta
            'RESET': '\033[0m'      # Reset
        }
        
        if hasattr(record, 'levelname'):
            color = colors.get(record.levelname, colors['RESET'])
            record.colored_levelname = f"{color}{record.levelname}{colors['RESET']}"
        
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    include_timestamp: bool = True,
    enable_colors: bool = True
) -> logging.Logger:
    """Configure application logging with enhanced formatting"""
    
    if format_string is None:
        if enable_colors:
            format_string = "%(timestamp)s - %(name)s - %(colored_levelname)s - %(message)s"
        else:
            format_string = "%(timestamp)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create custom formatter
    formatter = TechTestFormatter(format_string)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()  # Clear existing handlers
    root_logger.addHandler(console_handler)
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Create application logger
    logger = logging.getLogger("techtest")
    
    # Set level based on environment
    try:
        from config.settings import settings
        if settings.FLASK_ENV == "development":
            logger.setLevel(logging.DEBUG)
        elif settings.TESTING:
            logger.setLevel(logging.WARNING)
        else:
            logger.setLevel(logging.INFO)
    except ImportError:
        # Fallback if settings not available
        logger.setLevel(logging.INFO)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module"""
    return logging.getLogger(f"techtest.{name}")


def log_function_call(func_name: str, args: tuple = (), kwargs: Dict[str, Any] = None, logger_name: str = "api"):
    """Log function calls for debugging"""
    logger = get_logger(logger_name)
    kwargs = kwargs or {}
    
    # Sanitize sensitive data
    safe_kwargs = {}
    sensitive_keys = {'password', 'token', 'secret', 'key'}
    
    for key, value in kwargs.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            safe_kwargs[key] = "[REDACTED]"
        else:
            safe_kwargs[key] = value
    
    logger.debug(f"Calling {func_name}(args={args}, kwargs={safe_kwargs})")


def log_database_operation(operation: str, table: str, record_id: Any = None, extra_info: Dict[str, Any] = None):
    """Log database operations"""
    logger = get_logger("database")
    extra_info = extra_info or {}
    
    log_msg = f"DB {operation.upper()}: {table}"
    if record_id:
        log_msg += f" (id={record_id})"
    
    if extra_info:
        log_msg += f" - {extra_info}"
    
    logger.info(log_msg)


def log_api_request(method: str, endpoint: str, status_code: int, duration_ms: float = None):
    """Log API requests"""
    logger = get_logger("api")
    
    log_msg = f"{method} {endpoint} -> {status_code}"
    if duration_ms:
        log_msg += f" ({duration_ms:.2f}ms)"
    
    if status_code >= 400:
        logger.warning(log_msg)
    else:
        logger.info(log_msg)


# Global application logger
app_logger = setup_logging()


class LoggerMixin:
    """Mixin to add logging capabilities to classes"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        module_name = self.__class__.__module__.split('.')[-1]
        return get_logger(module_name)
    
    def log_operation(self, operation: str, **kwargs):
        """Log an operation with context"""
        class_name = self.__class__.__name__
        self.logger.info(f"{class_name}.{operation}", extra=kwargs)