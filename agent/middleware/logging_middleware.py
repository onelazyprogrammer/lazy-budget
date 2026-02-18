import time
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from agent.utils.logging import get_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses in standard FastAPI format."""

    def __init__(self, app):
        super().__init__(app)
        self.logger = get_logger(__name__)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Intercept request/response and log in combined format."""
        start_time = time.time()

        # Extract request info
        method = request.method
        path = request.url.path
        query_string = request.url.query
        full_path = f"{path}?{query_string}" if query_string else path

        # Call the actual endpoint
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            # Log exception and re-raise
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                f"{method} {full_path} - Exception: {type(e).__name__} - {duration_ms:.1f}ms"
            )
            raise

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log combined request/response on single line
        self._log_request_response(method, full_path, status_code, duration_ms)

        return response

    def _log_request_response(
        self, method: str, path: str, status_code: int, duration_ms: float
    ) -> None:
        """Log request and response in combined format (nginx-style access log)."""
        # Determine log level based on status code
        if status_code >= 500:
            log_level = self.logger.error
        elif status_code >= 400:
            log_level = self.logger.warning
        else:
            log_level = self.logger.info

        # Single line log: "POST /api/v1/auth/token - 200 - 45.3ms"
        log_level(f"{method} {path} - {status_code} - {duration_ms:.1f}ms")
