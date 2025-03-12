from typing import Dict, Any, ClassVar
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    """
    Centralized configuration for all microservices
    """
    # Common settings
    ENV: str = "development"
    DEBUG: bool = True
    SQL_DEBUG: bool = False
    
    # Service configurations
    SERVICES: Dict[str, Dict[str, Any]] = {
        "users": {
            "name": "Users Service",
            "version": "1.0.0",
            "api_prefix": "/api/v1",
            "port": 8000
        }
    }

    # Database settings
    DATABASE_CONFIG: ClassVar[Dict[str, Any]] = {
        "host": "mysql",
        "port": 3306,
        "user": "admin",
        "password": "123456",
        "database": "podv1"
    }
    DATABASE_URL: str = f"mysql+pymysql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}/{DATABASE_CONFIG['database']}"

    # Redis Configuration
    REDIS_CONFIG: ClassVar[Dict[str, Any]] = {
        "host": os.getenv('REDIS_HOST', 'redis'),
        "port": int(os.getenv('REDIS_PORT', 6379)),
        "password": os.getenv('REDIS_PASSWORD', '123456789'),
        "default_db": 0,
        "databases": {
            "rate_limit": 0,
            "cache": 1,
            "session": 2
        }
    }

    # Rate Limiting Settings
    RATE_LIMIT: Dict = {
        'REDIS_HOST': REDIS_CONFIG['host'],
        'REDIS_PORT': REDIS_CONFIG['port'],
        'REDIS_DB': REDIS_CONFIG['databases']['rate_limit'],
        'REDIS_PASSWORD': REDIS_CONFIG['password'],
        'RATE_LIMIT_WINDOW': int(os.getenv('RATE_LIMIT_WINDOW', 60)),
        'MAX_REQUESTS': int(os.getenv('MAX_REQUESTS', 100)),
        'REQUEST_COOLDOWN': int(os.getenv('REQUEST_COOLDOWN', 2))
    }

    # JWT settings
    JWT_SETTINGS: ClassVar[Dict[str, Any]] = {
        "SECRET_KEY": "your-secret-key-here",
        "ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
        "REFRESH_TOKEN_EXPIRE_DAYS": 7
    }

    # CORS Settings
    CORS: Dict = {
        'ALLOW_ORIGINS': [
            "http://localhost:3000",  # Frontend URL
            "http://localhost:8000",  # Backend URL
        ],
        'ALLOW_METHODS': ["*"],
        'ALLOW_HEADERS': ["*"],
        'ALLOW_CREDENTIALS': True
    }

    # Docker service configurations
    DOCKER_CONFIG: ClassVar[Dict[str, Dict[str, Any]]] = {
        "mysql": {
            "root_password": "rootpassword",
            "database": DATABASE_CONFIG["database"],
            "user": DATABASE_CONFIG["user"],
            "password": DATABASE_CONFIG["password"],
            "port": DATABASE_CONFIG["port"]
        },
        "redis": {
            "port": REDIS_CONFIG["port"],
            "password": REDIS_CONFIG["password"],
            "databases": 16  # Number of Redis databases
        },
        "adminer": {
            "port": 8080
        }
    }

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 