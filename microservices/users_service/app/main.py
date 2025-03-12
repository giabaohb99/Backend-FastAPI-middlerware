from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from op_core.core import settings, LoggingMiddleware, RateLimitMiddleware

from .api.v1 import api

# Get users service config
service_config = settings.SERVICES["users"]

app = FastAPI(
    title=service_config["name"],
    version=service_config["version"],
    openapi_url=f"{service_config['api_prefix']}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS['ALLOW_ORIGINS'],
    allow_credentials=settings.CORS['ALLOW_CREDENTIALS'],
    allow_methods=settings.CORS['ALLOW_METHODS'],
    allow_headers=settings.CORS['ALLOW_HEADERS'],
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Add request logging middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(
    api.router,
    prefix=service_config["api_prefix"],
    tags=["authentication"]
) 