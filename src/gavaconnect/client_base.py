from abc import ABC, abstractmethod
import base64
import time
from typing import Any, Optional, TypedDict

from .exceptions import AuthenticationError

ENVIRONMENTS = {
    "sandbox": "https://sbx.kra.go.ke",
    "production": "https://api.kra.go.ke",
}


class AuthConfig(TypedDict):
    consumer_key: str
    consumer_secret: str


class BaseGavaConnect(ABC):
    def __init__(
        self,
        environment: str = "sandbox",
        invoice: Optional[AuthConfig] = None,
        pin: Optional[AuthConfig] = None,
        station: Optional[AuthConfig] = None,
    ) -> None:
        if environment not in ENVIRONMENTS:
            raise ValueError(f"Environment must be one of: {list(ENVIRONMENTS.keys())}")

        self.base_url = ENVIRONMENTS[environment]
        self.configs = {
            "invoice": invoice,
            "pin": pin,
            "station": station,
        }
        self.token_cache: dict[str, dict[str, Any]] = {}

    def _get_auth_config(self, scope: str) -> AuthConfig:
        config = self.configs.get(scope)
        if (
            not config
            or "consumer_key" not in config
            or "consumer_secret" not in config
        ):
            raise AuthenticationError(
                f"Missing client credentials for application scope: '{scope}'"
            )
        return config

    def _cache_valid(self, scope: str) -> bool:
        cached = self.token_cache.get(scope)
        return bool(cached and cached.get("expires_at", 0) - time.time() > 60)

    def _store_token(self, scope: str, token_data: dict[str, Any]) -> str:
        access_token = token_data["access_token"]
        expires_in = int(token_data.get("expires_in", 3600))
        self.token_cache[scope] = {
            "access_token": access_token,
            "expires_at": time.time() + expires_in,
        }
        return access_token

    def _basic_auth_headers(self, scope: str) -> dict[str, str]:
        config = self._get_auth_config(scope)
        credentials = f"{config['consumer_key']}:{config['consumer_secret']}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}


class SyncGavaConnectBase(BaseGavaConnect, ABC):
    @abstractmethod
    def get_valid_token(self, scope: str) -> str:
        raise NotImplementedError


class AsyncGavaConnectBase(BaseGavaConnect, ABC):
    @abstractmethod
    async def get_valid_token(self, scope: str) -> str:
        raise NotImplementedError
