"""Custom exceptions for MCP Suno server."""


class SunoError(Exception):
    """Base exception for Suno API errors."""

    def __init__(self, message: str, code: str = "unknown"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class SunoAuthError(SunoError):
    """Authentication error."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, code="auth_error")


class SunoAPIError(SunoError):
    """API request error."""

    def __init__(
        self,
        message: str,
        code: str = "api_error",
        status_code: int | None = None,
        task_id: str | None = None,
        trace_id: str | None = None,
    ):
        self.status_code = status_code
        self.task_id = task_id
        self.trace_id = trace_id
        super().__init__(message, code)

    def __str__(self) -> str:
        identifiers = []
        if self.task_id:
            identifiers.append(f"task_id={self.task_id}")
        if self.trace_id:
            identifiers.append(f"trace_id={self.trace_id}")
        if not identifiers:
            return self.message
        return f"{self.message} (code={self.code}, {', '.join(identifiers)})"


class SunoValidationError(SunoError):
    """Validation error for request parameters."""

    def __init__(self, message: str):
        super().__init__(message, code="validation_error")


class SunoTimeoutError(SunoError):
    """Request timeout error."""

    def __init__(self, message: str = "Request timed out"):
        super().__init__(message, code="timeout_error")
