from .config import settings
from .database import Base, engine, get_db
from .error_handlers import (
    ErrorResponse,
    handle_validation_error,
    handle_request_validation_error,
    handle_http_exception,
    handle_generic_error
)
from .exceptions import (
    APIError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    DatabaseError
)
from .exception_handlers import (
    validation_error_handler,
    request_validation_error_handler,
    http_exception_handler,
    generic_error_handler
)

from .security import verify_password, get_password_hash, create_access_token, decode_token
from .middleware import LoggingMiddleware, SQLQueryLoggingMiddleware, RateLimitMiddleware
from .logging import log_customer_activity
# from .models.log import Log

__all__ = [
    'settings',
    'Base',
    'engine',
    'get_db',
    'ErrorResponse',
    'handle_validation_error',
    'handle_request_validation_error',
    'handle_http_exception',
    'handle_generic_error',
    'APIError',
    'AuthenticationError',
    'ValidationError',
    'NotFoundError',
    'DatabaseError',
    'LoggingMiddleware',
    'SQLQueryLoggingMiddleware',
    'RateLimitMiddleware',
    'create_access_token',
    'decode_token',
    'validation_error_handler',
    'request_validation_error_handler',
    'http_exception_handler',
    'generic_error_handler',
    'log_customer_activity'
]