from typing import TYPE_CHECKING, List
import httpx

from gavaconnect.exceptions import (
    InvalidObligationPINError,
    ValidationError,
    TransientError,
)
from gavaconnect.models import ObligationData, ObligationResponse

if TYPE_CHECKING:
    from gavaconnect.async_client import GavaConnect
    from gavaconnect.sync_client import GavaConnectSync


class ObligationAPI:
    """Asynchronous Tax Obligations Fetcher API Wrapper."""

    def __init__(self, client: "GavaConnect") -> None:
        self._client = client

    async def fetch(self, pin: str) -> List[ObligationData]:
        """Fetch the registered tax obligations for a given KRA PIN.

        Ref: https://sbx.kra.go.ke/dtd/checker/v1/obligation
        """
        token = await self._client.get_valid_token("obligation")
        url = f"{self._client.base_url}/dtd/checker/v1/obligation"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        payload = {"taxPayerPin": pin}

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

            if data.get("ResponseCode") == "20001" or data.get("Status") == "NOK":
                raise InvalidObligationPINError(
                    data.get("ResponseMsg", "Invalid KRA Pin provided")
                )

            validated = ObligationResponse.model_validate(data)
            return validated.obligations_list

        except httpx.HTTPError as e:
            raise TransientError(f"Transport network failure: {str(e)}") from e
        except Exception as e:
            if isinstance(e, (InvalidObligationPINError, TransientError)):
                raise
            raise ValidationError(f"Response serialization failed: {str(e)}") from e


class SyncObligationAPI:
    """Synchronous Tax Obligations Fetcher API Wrapper."""

    def __init__(self, client: "GavaConnectSync") -> None:
        self._client = client

    def fetch(self, pin: str) -> List[ObligationData]:
        """Fetch the registered tax obligations for a given KRA PIN synchronously."""
        token = self._client.get_valid_token("obligation")
        url = f"{self._client.base_url}/dtd/checker/v1/obligation"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        payload = {"taxPayerPin": pin}

        try:
            response = self._client.client.post(url, headers=headers, json=payload)

            if response.status_code >= 500:
                raise TransientError(
                    f"KRA gateway server error: {response.status_code}"
                )

            response.raise_for_status()
            data = response.json()

            if data.get("ResponseCode") == "20001" or data.get("Status") == "NOK":
                raise InvalidObligationPINError(
                    data.get("ResponseMsg", "Invalid KRA Pin provided")
                )

            validated = ObligationResponse.model_validate(data)
            return validated.obligations_list

        except httpx.HTTPError as e:
            raise TransientError(f"Transport network failure: {str(e)}") from e
        except Exception as e:
            if isinstance(e, (InvalidObligationPINError, TransientError)):
                raise
            raise ValidationError(f"Response serialization failed: {str(e)}") from e
