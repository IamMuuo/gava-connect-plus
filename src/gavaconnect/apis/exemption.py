from typing import TYPE_CHECKING
import httpx

from gavaconnect.exceptions import (
    ExemptionNotFoundError,
    GavaConnectError,
    InvalidExemptionPINError,
    TransientError,
    ValidationError,
)
from gavaconnect.models import ExemptionData

if TYPE_CHECKING:
    from gavaconnect.async_client import GavaConnect
    from gavaconnect.sync_client import GavaConnectSync


class ExemptionAPI:
    """Asynchronous Income Tax & VAT Exemption Checker API Wrapper."""

    def __init__(self, client: "GavaConnect") -> None:
        self._client = client

    async def check(self, pin: str) -> ExemptionData:
        """Verify whether a taxpayer holds a valid Income Tax/VAT exemption certificate.

        Ref: https://sbx.kra.go.ke/checker/v1/itexemption
        """
        token = await self._client.get_valid_token("exemption")
        url = f"{self._client.base_url}/checker/v1/itexemption"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        payload = {"pin": pin}

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

            response_code = str(data.get("response_code", "")).strip()
            response_message = data.get("response_message")

            if response_code == "600":
                raise InvalidExemptionPINError(response_message or "Invalid KRA PIN")
            elif response_code == "900":
                raise ExemptionNotFoundError(
                    response_message or "Invalid Exemption Certificate"
                )
            elif response_code and response_code != "200":
                raise GavaConnectError(
                    f"Unexpected exemption API response [{response_code}]: {response_message}"
                )

            return ExemptionData.model_validate(data)

        except httpx.HTTPError as e:
            raise TransientError(f"Transport network failure: {str(e)}") from e
        except Exception as e:
            if isinstance(
                e,
                (
                    InvalidExemptionPINError,
                    ExemptionNotFoundError,
                    TransientError,
                    GavaConnectError,
                ),
            ):
                raise
            raise ValidationError(f"Response serialization failed: {str(e)}") from e


class SyncExemptionAPI:
    """Synchronous Income Tax & VAT Exemption Checker API Wrapper."""

    def __init__(self, client: "GavaConnectSync") -> None:
        self._client = client

    def check(self, pin: str) -> ExemptionData:
        """Verify whether a taxpayer holds a valid Income Tax/VAT exemption certificate synchronously."""
        token = self._client.get_valid_token("exemption")
        url = f"{self._client.base_url}/checker/v1/itexemption"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        payload = {"pin": pin}

        try:
            response = self._client.client.post(url, headers=headers, json=payload)

            if response.status_code >= 500:
                raise TransientError(
                    f"KRA gateway server error: {response.status_code}"
                )

            response.raise_for_status()
            data = response.json()

            response_code = str(data.get("response_code", "")).strip()
            response_message = data.get("response_message")

            if response_code == "600":
                raise InvalidExemptionPINError(response_message or "Invalid KRA PIN")
            elif response_code == "900":
                raise ExemptionNotFoundError(
                    response_message or "Invalid Exemption Certificate"
                )
            elif response_code and response_code != "200":
                raise GavaConnectError(
                    f"Unexpected exemption API response [{response_code}]: {response_message}"
                )

            return ExemptionData.model_validate(data)

        except httpx.HTTPError as e:
            raise TransientError(f"Transport network failure: {str(e)}") from e
        except Exception as e:
            if isinstance(
                e,
                (
                    InvalidExemptionPINError,
                    ExemptionNotFoundError,
                    TransientError,
                    GavaConnectError,
                ),
            ):
                raise
            raise ValidationError(f"Response serialization failed: {str(e)}") from e
