from typing import Dict, Any, ClassVar
from pydantic_settings import BaseSettings

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

      # Security settings
    SECRET_KEY: str = "abc-giabao-1234"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"  # Thêm dòng này
    
    # Docker service configurations
    DOCKER_CONFIG: ClassVar[Dict[str, Dict[str, Any]]] = {
        "mysql": {
            "root_password": "rootpassword",
            "database": DATABASE_CONFIG["database"],
            "user": DATABASE_CONFIG["user"],
            "password": DATABASE_CONFIG["password"],
            "port": DATABASE_CONFIG["port"]
        },
        "adminer": {
            "port": 8080
        }
    }

    class Config:
        case_sensitive = True

settings = Settings() 