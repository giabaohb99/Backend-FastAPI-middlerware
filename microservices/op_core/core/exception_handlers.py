from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from pydantic import ValidationError
from .error_handlers import (
    handle_validation_error,
    handle_request_validation_error,
    handle_http_exception,
    handle_generic_error
)

async def validation_error_handler(request: Request, exc: ValidationError):
    error = handle_validation_error(exc)
    return JSONResponse(
        status_code=error.status_code,
        content=error.to_dict()
    )

async def request_validation_error_handler(request: Request, exc: RequestValidationError):
    error = handle_request_validation_error(exc)
    return JSONResponse(
        status_code=error.status_code,
        content=error.to_dict()
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    error = handle_http_exception(exc)
    return JSONResponse(
        status_code=error.status_code,
        content=error.to_dict()
    )

async def generic_error_handler(request: Request, exc: Exception):
    error = handle_generic_error(exc)
    return JSONResponse(
        status_code=error.status_code,
        content=error.to_dict()
    ) 