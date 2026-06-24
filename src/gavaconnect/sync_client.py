import httpx

from gavaconnect.apis.pin import SyncPinAPI

from .client_base import SyncGavaConnectBase
from .exceptions import AuthenticationError


class GavaConnectSync(SyncGavaConnectBase):
    """Core Synchronous GavaConnect SDK Client."""

    def __init__(
        self, *args, http_client: httpx.Client | None = None, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.client = http_client or httpx.Client()
        self._owns_client = http_client is None
        self.pin = SyncPinAPI(self)

    def get_valid_token(self, scope: str) -> str:
        if self._cache_valid(scope):
            return self.token_cache[scope]["access_token"]

        try:
            response = self.client.get(
                f"{self.base_url}/v1/token/generate",
                headers=self._basic_auth_headers(scope=scope),
                params={"grant_type": "client_credentials"},
            )

            if response.status_code == 401:
                try:
                    error_data = response.json()
                    message = error_data.get("errorMessage", "Invalid credentials")
                except Exception:
                    message = "Invalid credentials"
                raise AuthenticationError(f"Auth failed: {message}")

            response.raise_for_status()
            return self._store_token(scope, response.json())

        except httpx.TimeoutException as e:
            raise AuthenticationError(
                f"OAuth2 authentication timed out for scope '{scope}'"
            ) from e
        except httpx.HTTPStatusError as e:
            raise AuthenticationError(
                f"OAuth2 authentication failed for scope '{scope}': {e.response.status_code}"
            ) from e

    def close(self) -> None:
        if self._owns_client:
            self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
