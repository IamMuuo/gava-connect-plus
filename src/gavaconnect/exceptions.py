class GavaConnectError(Exception):
    """Base exception for all GavaConnect SDK errors."""

    def __init__(
        self,
        message: str = "",
        *,
        code: str | None = None,
        status_code: int | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class AuthenticationError(GavaConnectError):
    """Raised when fetching or refreshing an OAuth2 token fails."""

    pass


class APIError(GavaConnectError):
    """Raised for unexpected API responses."""


class RateLimitError(GavaConnectError):
    """Raised when the API rate limit is exceeded."""


class InvoiceNotFoundError(GavaConnectError):
    """Raised when the requested invoice does not exist (Response Code: 40001)."""

    pass


class TransientError(GavaConnectError):
    """Raised for server errors or timeouts where retrying is safe (Response Codes: 40005, 50000)."""

    pass


class ValidationError(GavaConnectError):
    """Raised when a gateway response fails Pydantic schema validation."""

    pass
