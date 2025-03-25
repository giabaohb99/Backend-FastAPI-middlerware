from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
from pydantic import ValidationError
from op_core.core import (
    settings,
    LoggingMiddleware,
    RateLimitMiddleware,
    Base,
    engine,
    validation_error_handler,
    request_validation_error_handler,
    http_exception_handler,
    generic_error_handler
)
from .api.v1.customer import router as customer_router
# from .api.v1.otp import router as otp_router
from op_core.core.error_handlers import ErrorResponse

# Create all tables
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.SERVICES["customers"]["name"],
    version=settings.SERVICES["customers"]["version"],
    openapi_url=f"{settings.SERVICES['customers']['api_prefix']}/openapi.json"
)



# # Set all CORS enabled origins
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.CORS['ALLOW_ORIGINS'],
#     allow_credentials=settings.CORS['ALLOW_CREDENTIALS'],
#     allow_methods=settings.CORS['ALLOW_METHODS'],
#     allow_headers=settings.CORS['ALLOW_HEADERS'],
# )

# Add rate limiting middleware
# app.add_middleware(RateLimitMiddleware)

# Add request logging middleware
# app.add_middleware(LoggingMiddleware)

# # Exception handlers
# app.add_exception_handler(ValidationError, validation_error_handler)
# app.add_exception_handler(RequestValidationError, request_validation_error_handler)
# app.add_exception_handler(HTTPException, http_exception_handler)
# app.add_exception_handler(Exception, generic_error_handler)

# # Include routers
app.include_router(
    customer_router,
    prefix=f"{settings.SERVICES['customers']['api_prefix']}/customers",
    tags=["customers"]
)
# app.include_router(
#     otp_router,
#     prefix=f"{settings.SERVICES['users']['api_prefix']}/otp",
#     tags=["otp"]
# )

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "users_service"
    } 