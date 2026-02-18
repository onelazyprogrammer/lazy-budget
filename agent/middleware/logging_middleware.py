import time
import json
import logging
from typing import Callable, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses with sensitive field scrubbing."""

    # Fields to scrub in request bodies
    SENSITIVE_FIELDS = {
        "password",
        "hashed_password",
        "token",
        "access_token",
        "refresh_token",
    }

    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger(__name__)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Intercept request/response and log details."""
        start_time = time.time()

        # Extract request info
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params) if request.query_params else {}
        client_host = request.client.host if request.client else "unknown"
        content_type = request.headers.get("content-type", "")

        # Log user-agent if present
        user_agent = request.headers.get("user-agent", "")

        # Extract request body if applicable
        request_body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                if "application/json" in content_type:
                    body_bytes = await request.body()
                    if body_bytes:
                        request_body = json.loads(body_bytes)
                        # Scrub sensitive fields
                        request_body = self._scrub_sensitive_fields(request_body)
                elif "multipart/form-data" in content_type:
                    # Don't log file contents, just metadata
                    form_data = await request.form()
                    request_body = {
                        "multipart_form": {
                            "fields": list(form_data.keys()),
                            "file_count": sum(
                                1
                                for v in form_data.values()
                                if hasattr(v, "filename")
                            ),
                        }
                    }
            except Exception as e:
                request_body = f"<error reading body: {str(e)}>"

        # Log request
        request_log = {
            "event": "http_request",
            "method": method,
            "path": path,
            "query_params": query_params if query_params else None,
            "client_ip": client_host,
            "user_agent": user_agent if user_agent else None,
            "content_type": content_type if content_type else None,
        }
        if request_body is not None:
            request_log["body"] = request_body

        self._log_with_extra(logging.INFO, "HTTP Request", request_log)

        # Call the actual endpoint
        try:
            # Note: request body is cached by Starlette after first read
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            # Log exceptions
            self._log_with_extra(
                logging.ERROR,
                f"Unhandled exception in request {method} {path}",
                {
                    "method": method,
                    "path": path,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            raise

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Determine log level based on status code
        if status_code >= 500:
            log_level = logging.ERROR
        elif status_code >= 400:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO

        # Log response
        response_log = {
            "event": "http_response",
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
        }

        self._log_with_extra(log_level, "HTTP Response", response_log)

        return response

    def _scrub_sensitive_fields(self, data: Any) -> Any:
        """Recursively scrub sensitive fields from request data."""
        if isinstance(data, dict):
            scrubbed = {}
            for key, value in data.items():
                if key.lower() in self.SENSITIVE_FIELDS or key == "authorization":
                    scrubbed[key] = "***"
                elif isinstance(value, (dict, list)):
                    scrubbed[key] = self._scrub_sensitive_fields(value)
                else:
                    scrubbed[key] = value
            return scrubbed
        elif isinstance(data, list):
            return [
                self._scrub_sensitive_fields(item) for item in data
            ]
        else:
            return data

    def _log_with_extra(
        self, level: int, message: str, extra_data: dict
    ) -> None:
        """Log with extra context fields."""
        record = self.logger.makeRecord(
            self.logger.name,
            level,
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=None,
            extra=extra_data,
        )
        self.logger.handle(record)
