"""Structured error handling for MindMesh API.

Conforms to Specification v3 Section 11.13:
{"error": {"code": str, "message": str, "details": any}}
No stack traces or secrets are ever leaked in responses.
"""

from typing import Any, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class BadRequestError(AppError):
    def __init__(self, message: str, code: str = "BAD_REQUEST", details: Optional[Any] = None) -> None:
        super().__init__(message=message, code=code, status_code=status.HTTP_400_BAD_REQUEST, details=details)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Authentication required", code: str = "UNAUTHORIZED", details: Optional[Any] = None) -> None:
        super().__init__(message=message, code=code, status_code=status.HTTP_401_UNAUTHORIZED, details=details)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Access forbidden", code: str = "FORBIDDEN", details: Optional[Any] = None) -> None:
        super().__init__(message=message, code=code, status_code=status.HTTP_403_FORBIDDEN, details=details)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", code: str = "NOT_FOUND", details: Optional[Any] = None) -> None:
        super().__init__(message=message, code=code, status_code=status.HTTP_404_NOT_FOUND, details=details)


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict or duplicate state", code: str = "CONFLICT", details: Optional[Any] = None) -> None:
        super().__init__(message=message, code=code, status_code=status.HTTP_409_CONFLICT, details=details)


def format_error_response(code: str, message: str, details: Optional[Any] = None) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
        }
    }


def register_error_handlers(app: FastAPI) -> None:
    """Register uniform error handlers for all exceptions."""

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=format_error_response(code=exc.code, message=exc.message, details=exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        # Format Pydantic validation errors cleanly without exposing internals
        simplified_errors = [
            {
                "loc": [str(loc) for loc in err.get("loc", [])],
                "msg": err.get("msg", ""),
                "type": err.get("type", ""),
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=format_error_response(
                code="VALIDATION_ERROR",
                message="Request payload validation failed",
                details=simplified_errors,
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code_map = {
            status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
            status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
            status.HTTP_403_FORBIDDEN: "FORBIDDEN",
            status.HTTP_404_NOT_FOUND: "NOT_FOUND",
            status.HTTP_405_METHOD_NOT_ALLOWED: "METHOD_NOT_ALLOWED",
            status.HTTP_409_CONFLICT: "CONFLICT",
            status.HTTP_422_UNPROCESSABLE_ENTITY: "VALIDATION_ERROR",
        }
        if isinstance(exc.detail, dict):
            code = exc.detail.get("code", code_map.get(exc.status_code, "HTTP_ERROR"))
            message = exc.detail.get("message", "HTTP error")
            details = exc.detail.get("details", None)
        else:
            code = code_map.get(exc.status_code, "HTTP_ERROR")
            message = exc.detail if isinstance(exc.detail, str) else "HTTP error"
            details = exc.detail if not isinstance(exc.detail, str) else None
        return JSONResponse(
            status_code=exc.status_code,
            content=format_error_response(code=code, message=message, details=details),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        # Never leak traceback or sensitive details in 500 responses
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=format_error_response(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred",
                details=None,
            ),
        )
