import time
import json
from typing import Callable, Any, Dict
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
        """Intercept request/response and log with request/response indicators."""
        start_time = time.time()

        # Extract request info
        method = request.method
        path = request.url.path
        query_string = request.url.query
        full_path = f"{path}?{query_string}" if query_string else path

        # Extract headers
        headers_info = self._extract_headers(request.headers)

        # Extract body/params
        body_info = ""
        if method in ["POST", "PUT", "PATCH"]:
            body_data = await self._extract_body(request)
            if body_data:
                body_info = f" | body: {body_data}"

        # Log incoming request
        log_message = f"[REQUEST] {method} {full_path}"
        if headers_info:
            log_message += f" | headers: {headers_info}"
        if body_info:
            log_message += body_info

        self.logger.info(log_message)

        # Call the actual endpoint
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            # Log exception and re-raise
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                f"[RESPONSE] {method} {full_path} - Exception: {type(e).__name__} - {duration_ms:.1f}ms"
            )
            raise

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log response
        self._log_response(method, full_path, status_code, duration_ms)

        return response

    def _extract_headers(self, headers: Any) -> str:
        """Extract important headers for logging."""
        important_headers = {}

        # Headers to log
        header_names = ["user-agent", "content-type", "authorization"]
        for header_name in header_names:
            value = headers.get(header_name)
            if value:
                # Mask authorization token
                if header_name == "authorization":
                    value = "Bearer ***"
                important_headers[header_name] = value

        if important_headers:
            return str(important_headers)
        return ""

    async def _extract_body(self, request: Request) -> str:
        """Extract request body/params for logging."""
        try:
            content_type = request.headers.get("content-type", "")

            if "application/json" in content_type:
                body_bytes = await request.body()
                if body_bytes:
                    body_data = json.loads(body_bytes)
                    # Format as key=value pairs
                    params = self._format_params(body_data)
                    return params

            elif "application/x-www-form-urlencoded" in content_type:
                form_data = await request.form()
                params_dict = {k: form_data[k] for k in form_data.keys()}
                params = self._format_params(params_dict)
                return params

        except Exception:
            pass

        return ""

    def _format_params(self, data: Dict[str, Any]) -> str:
        """Format parameters as key=value string, handling nested objects."""
        params = []
        for k, v in data.items():
            # Skip sensitive fields
            if k.lower() in ["password", "hashed_password", "token", "access_token"]:
                params.append(f"{k}=***")
            elif isinstance(v, (dict, list)):
                # For complex types, just show type
                params.append(f"{k}=<{type(v).__name__}>")
            else:
                params.append(f"{k}={v}")
        return "{" + ", ".join(params) + "}"

    def _log_response(
        self, method: str, path: str, status_code: int, duration_ms: float
    ) -> None:
        """Log response with status code and duration."""
        # Determine log level based on status code
        if status_code >= 500:
            log_level = self.logger.error
        elif status_code >= 400:
            log_level = self.logger.warning
        else:
            log_level = self.logger.info

        # Response log: "[RESPONSE] POST /api/v1/auth/token - 201 - 45.3ms"
        log_level(f"[RESPONSE] {method} {path} - {status_code} - {duration_ms:.1f}ms")
