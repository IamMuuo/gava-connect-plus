from typing import TYPE_CHECKING
import httpx

from gavaconnect.exceptions import (
    InvalidPINError,
    ValidationError,
    TransientError,
)
from gavaconnect.models import PinData, PinResponse

if TYPE_CHECKING:
    from gavaconnect.async_client import GavaConnect
    from gavaconnect.sync_client import GavaConnectSync


class PinAPI:
    """Asynchronous PIN Checker API Wrapper."""

    def __init__(self, client: "GavaConnect") -> None:
        self._client = client

    async def check(self, pin: str) -> PinData:
        """Verify that a KRA PIN is registered and active.

        Ref: https://sbx.kra.go.ke/checker/v1/pinbypin
        """
        token = await self._client.get_valid_token("pin")
        url = f"{self._client.base_url}/checker/v1/pinbypin"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        payload = {"KRAPIN": pin}

        try:
            response = await self._client.client.post(
                url, headers=headers, json=payload
            )

            if response.status_code >= 500:
                raise TransientError(
                    f"KRA gateway server error: {response.status_code}"
                )

            response.raise_for_status()
            data = response.json()

            # Handle KRA's structural business logic errors
            if data.get("ResponseCode") == "19005" or data.get("Status") == "NOK":
                raise InvalidPINError(data.get("Message", "Invalid PIN provided"))

            validated = PinResponse.model_validate(data)
            return validated.pin_data

        except httpx.HTTPError as e:
            raise TransientError(f"Transport network failure: {str(e)}") from e
        except Exception as e:
            if isinstance(e, (InvalidPINError, TransientError)):
                raise
            raise ValidationError(f"Response serialization failed: {str(e)}") from e


class SyncPinAPI:
    """Synchronous PIN Checker API Wrapper."""

    def __init__(self, client: "GavaConnectSync") -> None:
        self._client = client

    def check(self, pin: str) -> PinData:
        """Verify that a KRA PIN is registered and active synchronously."""
        token = self._client.get_valid_token("pin")
        url = f"{self._client.base_url}/checker/v1/pinbypin"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        payload = {"KRAPIN": pin}

        try:
            response = self._client.client.post(url, headers=headers, json=payload)

            if response.status_code >= 500:
                raise TransientError(
                    f"KRA gateway server error: {response.status_code}"
                )

            response.raise_for_status()
            data = response.json()

            if data.get("ResponseCode") == "19005" or data.get("Status") == "NOK":
                raise InvalidPINError(data.get("Message", "Invalid PIN provided"))

            validated = PinResponse.model_validate(data)
            return validated.pin_data

        except httpx.HTTPError as e:
            raise TransientError(f"Transport network failure: {str(e)}") from e
        except Exception as e:
            if isinstance(e, (InvalidPINError, TransientError)):
                raise
            raise ValidationError(f"Response serialization failed: {str(e)}") from e
