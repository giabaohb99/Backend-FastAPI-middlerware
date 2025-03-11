from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from op_core.core import settings, log_request_middleware

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.middleware("http")(log_request_middleware)

# Include routers
app.include_router(
    api.router,
    prefix=service_config["api_prefix"],
    tags=["authentication"]
) 