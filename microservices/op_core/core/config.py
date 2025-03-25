from typing import Dict, Any
import os
from urllib.parse import quote_plus
from enum import IntEnum

  
class Settings:
    """
    Centralized configuration for all microservices
    """
    def __init__(self):
        # Common settings
        self.ENV = "development"
        self.DEBUG = True
        self.SQL_DEBUG = False
        
        # Service configurations
        self.SERVICES = {
            "users": {
                "name": "Users Service",
                "version": "1.0.0",
                "api_prefix": "/api/v1",
                "port": 8000
            },
            "employee": {
                "name": "Employee Service",
                "version": "1.0.0",
                "api_prefix": "/api/v1",
                "port": 8001
            },
            "customers": {
                "name": "Customers Service",
                "version": "1.0.0",
                "api_prefix": "/api/v1",
                "port": 8002
            }
        }

        # Database settings
        # AVNS
        # _lAfoL7_
        # p7q3u4Nj8yl4
        # lấy 3 dòng đầu thành chuỗi là matkhau, con duoi là port
        # 18336
        self.DATABASE_CONFIG = {
            "host": os.getenv('MYSQL_HOST', 'db1832025-hb-fd17.e.aivencloud.com'),
            "port": int(os.getenv('MYSQL_PORT', 'your_port')),
            "user": os.getenv('MYSQL_USER', 'appuser'),
            "password": os.getenv('MYSQL_PASSWORD', 'your_pass'),
            "database": os.getenv('MYSQL_DATABASE', 'defaultdb')
        }



        # Redis Configuration
        self.REDIS_CONFIG = {
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
        self.RATE_LIMIT = {
            'REDIS_HOST': self.REDIS_CONFIG['host'],
            'REDIS_PORT': self.REDIS_CONFIG['port'],
            'REDIS_DB': self.REDIS_CONFIG['databases']['rate_limit'],
            'REDIS_PASSWORD': self.REDIS_CONFIG['password'],
            'RATE_LIMIT_WINDOW': int(os.getenv('RATE_LIMIT_WINDOW', 60)),
            'MAX_REQUESTS': int(os.getenv('MAX_REQUESTS', 100)),
            'REQUEST_COOLDOWN': int(os.getenv('REQUEST_COOLDOWN', 5))
        }

        # JWT settings
        self.JWT_SETTINGS = {
            "SECRET_KEY": "giabao-test123",
            "ALGORITHM": "HS256",
            "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
            "REFRESH_TOKEN_EXPIRE_DAYS": 7
        }

        # CORS Settings
        self.CORS = {
            'ALLOW_ORIGINS': ["*"],  # Allow all origins in development
            'ALLOW_METHODS': ["*"],
            'ALLOW_HEADERS': ["*"],
            'ALLOW_CREDENTIALS': True
        }

        # Docker service configurations
        self.DOCKER_CONFIG = {
            "redis": {
                "port": self.REDIS_CONFIG["port"],
                "password": self.REDIS_CONFIG["password"],
                "databases": 16  # Number of Redis databases
            },
            "adminer": {
                "port": 8080
            }
        }

    @property
    def DATABASE_URL(self) -> str:
        password = quote_plus(self.DATABASE_CONFIG["password"])
        return (
            f"mysql+pymysql://{self.DATABASE_CONFIG['user']}:{password}@"
            f"{self.DATABASE_CONFIG['host']}:{self.DATABASE_CONFIG['port']}/"
            f"{self.DATABASE_CONFIG['database']}?ssl=true"
        )

settings = Settings()