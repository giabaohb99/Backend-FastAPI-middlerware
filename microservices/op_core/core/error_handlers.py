from fastapi import HTTPException, status
from typing import Any, Dict, List, Optional
from pydantic import ValidationError
from .config import settings

class ErrorResponse(Exception):
    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: str,
        details: Optional[List[Dict[str, Any]]] = None,
        location: Optional[str] = None
    ):
        self.status_code = status_code
        self.message = message
        self.error_code = error_code
        self.details = details or []
        self.location = location

    def to_dict(self) -> Dict[str, Any]:
        response = {
            "status": "error",
            "code": self.error_code,
            "message": self.message,
            "details": self.details if settings.ENV == "development" else []
        }
        if settings.ENV == "development" and self.location:
            response["location"] = self.location
        return response

def handle_validation_error(exc: ValidationError) -> ErrorResponse:
    details = []
    for error in exc.errors():
        detail = {
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        }
        details.append(detail)
    
    return ErrorResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Validation error",
        error_code="VALIDATION_ERROR",
        details=details,
        location="request_validation"
    )

def handle_request_validation_error(exc: Any) -> ErrorResponse:
    details = []
    for error in exc.errors():
        detail = {
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        }
        details.append(detail)
    
    return ErrorResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        message="Invalid request format",
        error_code="INVALID_REQUEST",
        details=details,
        location="request_validation"
    )

def handle_http_exception(exc: HTTPException) -> ErrorResponse:
    return ErrorResponse(
        status_code=exc.status_code,
        message=str(exc.detail),
        error_code="HTTP_ERROR",
        location="http_exception"
    )

def handle_generic_error(exc: Exception) -> ErrorResponse:
    return ErrorResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Internal server error",
        error_code="INTERNAL_ERROR",
        details=[{"error": str(exc)}] if settings.ENV == "development" else None,
        location=f"{exc.__class__.__module__}.{exc.__class__.__name__}"
    )
