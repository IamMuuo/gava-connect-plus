from .async_client import GavaConnect
from .sync_client import GavaConnectSync

from .exceptions import (
    GavaConnectError,
    AuthenticationError,
    InvoiceNotFoundError,
    TransientError,
    ValidationError,
    APIError,
    RateLimitError,
    InvalidPINError,
    InvalidTaxpayerIDError,
    InvalidStationPINError,
)

__all__ = [
    "GavaConnect",
    "GavaConnectSync",
    "GavaConnectError",
    "AuthenticationError",
    "InvoiceNotFoundError",
    "TransientError",
    "ValidationError",
    "RateLimitError",
    "APIError",
    "InvalidTaxpayerIDError",
    "InvalidPINError",
    "InvalidStationPINError",
]


def hello() -> str:
    return "Hello from gava-connect-plus!"
