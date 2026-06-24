from typing import TYPE_CHECKING
import httpx

from gavaconnect.exceptions import (
    GavaConnectError,
    TaxpayerNotFoundError,
    TransientError,
    ValidationError,
)
from gavaconnect.models import PinLookupResponse, TaxpayerType

if TYPE_CHECKING:
    from gavaconnect.async_client import GavaConnect
    from gavaconnect.sync_client import GavaConnectSync


class PinLookupAPI:
    """Asynchronous PIN Checker BY ID API Wrapper."""

    def __init__(self, client: "GavaConnect") -> None:
        self._client = client

    async def by_id(
        self, taxpayer_id: str, taxpayer_type: TaxpayerType = "KE"
    ) -> PinLookupResponse:
        """Resolve a KRA PIN using an ID asynchronously."""
        token = await self._client.get_valid_token("pin_lookup")
        url = f"{self._client.base_url}/checker/v1/pin"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        payload = {"TaxpayerType": taxpayer_type, "TaxpayerID": taxpayer_id}

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

            error_code = data.get("ErrorCode") or data.get("errorCode")
            error_msg = data.get("ErrorMessage") or data.get("errorMessage")

            if error_code is not None:
                error_code_str = str(error_code)
                if str(error_code) == "30002":
                    raise TaxpayerNotFoundError(error_msg or "Taxpayer ID not found.")
                elif error_code_str == "400":
                    raise ValidationError(
                        error_msg or "Missing mandatory payload parameter."
                    )

                raise GavaConnectError(f"API Error {error_code}: {error_msg}")

            return PinLookupResponse.model_validate(data)

        except httpx.HTTPError as e:
            raise TransientError(f"Transport network failure: {e}") from e


class SyncPinLookupAPI:
    """Synchronous PIN Checker BY ID API Wrapper."""

    def __init__(self, client: "GavaConnectSync") -> None:
        self._client = client

    def by_id(
        self, taxpayer_id: str, taxpayer_type: TaxpayerType = "KE"
    ) -> PinLookupResponse:
        """Resolve a KRA PIN using an ID synchronously."""
        token = self._client.get_valid_token("pin_lookup")
        url = f"{self._client.base_url}/checker/v1/pin"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        payload = {"TaxpayerType": taxpayer_type, "TaxpayerID": taxpayer_id}

        try:
            response = self._client.client.post(url, headers=headers, json=payload)
            if response.status_code >= 500:
                raise TransientError(
                    f"KRA gateway server error: {response.status_code}"
                )

            response.raise_for_status()
            data = response.json()

            error_code = data.get("ErrorCode") or data.get("errorCode")
            error_msg = data.get("ErrorMessage") or data.get("errorMessage")

            if error_code is not None:
                error_code_str = str(error_code)
                if error_code_str == "30002":
                    raise TaxpayerNotFoundError(error_msg or "Taxpayer ID not found.")
                elif error_code_str == "400":
                    raise ValidationError(
                        error_msg or "Missing mandatory payload parameter."
                    )
                raise GavaConnectError(f"API Error {error_code_str}: {error_msg}")

            return PinLookupResponse.model_validate(data)

        except httpx.HTTPError as e:
            raise TransientError(f"Transport network failure: {e}") from e
