from typing import TYPE_CHECKING
import httpx

from gavaconnect.exceptions import (
    InvalidExciseLicenseError,
    TransientError,
    ValidationError,
)
from gavaconnect.models import ExciseLicenseData, ExciseLicenseResponse

if TYPE_CHECKING:
    from gavaconnect.async_client import GavaConnect
    from gavaconnect.sync_client import GavaConnectSync


class ExciseLicenseAPI:
    """Asynchronous Excise License Checker By Certificate Number API Wrapper."""

    def __init__(self, client: "GavaConnect") -> None:
        self._client = client

    async def check_by_number(self, excise_licence_no: str) -> ExciseLicenseData:
        """Verify the validity of an Excise License Certificate Number.

        Ref: https://sbx.kra.go.ke/checker/v1/ExciseLicenseByNum
        """
        token = await self._client.get_valid_token("excise_license")
        url = f"{self._client.base_url}/checker/v1/ExciseLicenseByNum"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        payload = {"ExciseLicenceNo": excise_licence_no}

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

            if data.get("ResponseCode") == "80002" or data.get("Status") == "NOK":
                raise InvalidExciseLicenseError(
                    data.get("Message", "Invalid Excise License Number")
                )

            validated = ExciseLicenseResponse.model_validate(data)
            return validated.excise_license_data

        except httpx.HTTPError as e:
            raise TransientError(f"Transport network failure: {str(e)}") from e
        except Exception as e:
            if isinstance(e, (InvalidExciseLicenseError, TransientError)):
                raise
            raise ValidationError(f"Response serialization failed: {str(e)}") from e


class SyncExciseLicenseAPI:
    """Synchronous Excise License Checker By Certificate Number API Wrapper."""

    def __init__(self, client: "GavaConnectSync") -> None:
        self._client = client

    def check_by_number(self, excise_licence_no: str) -> ExciseLicenseData:
        """Verify the validity of an Excise License Certificate Number synchronously."""
        token = self._client.get_valid_token("excise_license")
        url = f"{self._client.base_url}/checker/v1/ExciseLicenseByNum"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        payload = {"ExciseLicenceNo": excise_licence_no}

        try:
            response = self._client.client.post(url, headers=headers, json=payload)

            if response.status_code >= 500:
                raise TransientError(
                    f"KRA gateway server error: {response.status_code}"
                )

            response.raise_for_status()
            data = response.json()

            if data.get("ResponseCode") == "80002" or data.get("Status") == "NOK":
                raise InvalidExciseLicenseError(
                    data.get("Message", "Invalid Excise License Number")
                )

            validated = ExciseLicenseResponse.model_validate(data)
            return validated.excise_license_data

        except httpx.HTTPError as e:
            raise TransientError(f"Transport network failure: {str(e)}") from e
        except Exception as e:
            if isinstance(e, (InvalidExciseLicenseError, TransientError)):
                raise
            raise ValidationError(f"Response serialization failed: {str(e)}") from e
