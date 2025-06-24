"""
Custom exception handlers
"""
from fastapi import FastAPI
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
) -> JSONResponse:
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "request_id": getattr(request.state, "request_id", None)
            }
        }
    )

async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": 422,
                "message": "Validation failed",
                "details": errors,
                "request_id": getattr(request.state, "request_id", None)
            }
        }
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle unexpected exceptions"""
    logger.error(
        f"Unhandled exception",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=exc
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "request_id": getattr(request.state, "request_id", None)
            }
        }
    )


class MCPException(Exception):
    """Base exception for MCP application"""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "MCP_ERROR"
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)


class ProjectNotFoundError(MCPException):
    """Project not found"""
    def __init__(self, project_id: int):
        super().__init__(
            message=f"Project with ID {project_id} not found",
            status_code=404,
            error_code="PROJECT_NOT_FOUND"
        )


class AnalysisTimeoutError(MCPException):
    """Analysis timeout"""
    def __init__(self, timeout: int):
        super().__init__(
            message=f"Analysis timed out after {timeout} seconds",
            status_code=408,
            error_code="ANALYSIS_TIMEOUT"
        )


class InvalidFileError(MCPException):
    """Invalid file for analysis"""
    def __init__(self, reason: str):
        super().__init__(
            message=f"Invalid file: {reason}",
            status_code=400,
            error_code="INVALID_FILE"
        )


async def mcp_exception_handler(
    request: Request,
    exc: MCPException
) -> JSONResponse:
    """Handle MCP custom exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "error_code": exc.error_code,
                "message": exc.message,
                "request_id": getattr(request.state, "request_id", None)
            }
        }
    )


def setup_exception_handlers(app: FastAPI):
    """Setup all exception handlers"""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(MCPException, mcp_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)