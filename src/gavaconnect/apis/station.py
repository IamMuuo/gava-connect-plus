from typing import TYPE_CHECKING
import httpx

from gavaconnect.exceptions import (
    InvalidStationPINError,
    ValidationError,
    TransientError,
    GavaConnectError,
)
from gavaconnect.models import StationData, StationResponse

if TYPE_CHECKING:
    from gavaconnect.async_client import GavaConnect
    from gavaconnect.sync_client import GavaConnectSync


class StationAPI:
    """Asynchronous KRA Tax Station Checker API Wrapper."""

    def __init__(self, client: "GavaConnect") -> None:
        self._client = client

    async def get(self, pin: str) -> StationData:
        """Fetch the registered Tax Service Office (Station Name) for a given KRA PIN.

        Ref: https://sbx.kra.go.ke/dtd/checker/v1/station
        """
        token = await self._client.get_valid_token("station")
        url = f"{self._client.base_url}/dtd/checker/v1/station"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        payload = {"kraPin": pin}

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

            # Accommodating potential variations in error formats
            error_code = str(data.get("ResponseCode", data.get("ErrorCode", "")))
            error_msg = data.get("Message", data.get("ErrorMessage", ""))

            if error_code == "84002" or data.get("Status") == "NOK":
                raise InvalidStationPINError(
                    error_msg or "Inactive or Wrong PIN provided."
                )
            elif error_code and error_code != "84000":
                raise GavaConnectError(
                    f"Unexpected station API error [{error_code}]: {error_msg}"
                )

            validated = StationResponse.model_validate(data)
            return validated.station_data

        except httpx.HTTPError as e:
            raise TransientError(f"Transport network failure: {str(e)}") from e
        except Exception as e:
            if isinstance(
                e, (InvalidStationPINError, TransientError, GavaConnectError)
            ):
                raise
            raise ValidationError(f"Response serialization failed: {str(e)}") from e


class SyncStationAPI:
    """Synchronous KRA Tax Station Checker API Wrapper."""

    def __init__(self, client: "GavaConnectSync") -> None:
        self._client = client

    def get(self, pin: str) -> StationData:
        """Fetch the registered Tax Service Office (Station Name) synchronously."""
        token = self._client.get_valid_token("station")
        url = f"{self._client.base_url}/dtd/checker/v1/station"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        payload = {"kraPin": pin}

        try:
            response = self._client.client.post(url, headers=headers, json=payload)

            if response.status_code >= 500:
                raise TransientError(
                    f"KRA gateway server error: {response.status_code}"
                )

            response.raise_for_status()
            data = response.json()

            error_code = str(data.get("ResponseCode", data.get("ErrorCode", "")))
            error_msg = data.get("Message", data.get("ErrorMessage", ""))

            if error_code == "84002" or data.get("Status") == "NOK":
                raise InvalidStationPINError(
                    error_msg or "Inactive or Wrong PIN provided."
                )
            elif error_code and error_code != "84000":
                raise GavaConnectError(
                    f"Unexpected station API error [{error_code}]: {error_msg}"
                )

            validated = StationResponse.model_validate(data)
            return validated.station_data

        except httpx.HTTPError as e:
            raise TransientError(f"Transport network failure: {str(e)}") from e
        except Exception as e:
            if isinstance(
                e, (InvalidStationPINError, TransientError, GavaConnectError)
            ):
                raise
            raise ValidationError(f"Response serialization failed: {str(e)}") from e
