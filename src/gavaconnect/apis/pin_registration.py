from typing import TYPE_CHECKING
import httpx

from gavaconnect.exceptions import (
    GavaConnectError,
    PinRegistrationValidationError,
    TransientError,
    ValidationError,
)
from gavaconnect.models import (
    IsPinWithNoObligation,
    PinRegistrationResponse,
    PinRegistrationResult,
    TaxpayerType,
)

if TYPE_CHECKING:
    from gavaconnect.async_client import GavaConnect
    from gavaconnect.sync_client import GavaConnectSync


class PinRegistrationAPI:
    """Asynchronous Individual KRA PIN Registration API Wrapper."""

    def __init__(self, client: "GavaConnect") -> None:
        self._client = client

    async def register(
        self,
        taxpayer_type: TaxpayerType,
        identification_number: str,
        date_of_birth: str,
        mobile_number: str,
        email_address: str,
        is_pin_with_no_obligation: IsPinWithNoObligation = "No",
    ) -> PinRegistrationResult:
        """Register a new individual KRA PIN.

        Ref: https://sbx.kra.go.ke/v1/generate/pin
        """
        token = await self._client.get_valid_token("pin_registration")
        url = f"{self._client.base_url}/v1/generate/pin"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        payload = {
            "TAXPAYERDETAILS": {
                "TaxpayerType": taxpayer_type,
                "IdentificationNumber": identification_number,
                "DateOfBirth": date_of_birth,
                "MobileNumber": mobile_number,
                "EmailAddress": email_address,
                "IsPinWithNoOblig": is_pin_with_no_obligation,
            }
        }

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

            error_code = data.get("ErrorCode")
            if error_code is not None:
                error_msg = data.get("ErrorMessage")
                if str(error_code).strip() == "80002":
                    raise PinRegistrationValidationError(
                        error_msg or "Data Validation Error"
                    )
                raise GavaConnectError(f"API Error {error_code}: {error_msg}")

            validated = PinRegistrationResponse.model_validate(data)
            result = validated.result

            if result.status.upper() == "NOK":
                raise PinRegistrationValidationError(
                    result.message or "PIN registration failed"
                )

            return result

        except httpx.HTTPError as e:
            raise TransientError(f"Transport network failure: {str(e)}") from e
        except Exception as e:
            if isinstance(
                e, (PinRegistrationValidationError, TransientError, GavaConnectError)
            ):
                raise
            raise ValidationError(f"Response serialization failed: {str(e)}") from e


class SyncPinRegistrationAPI:
    """Synchronous Individual KRA PIN Registration API Wrapper."""

    def __init__(self, client: "GavaConnectSync") -> None:
        self._client = client

    def register(
        self,
        taxpayer_type: TaxpayerType,
        identification_number: str,
        date_of_birth: str,
        mobile_number: str,
        email_address: str,
        is_pin_with_no_obligation: IsPinWithNoObligation = "No",
    ) -> PinRegistrationResult:
        """Register a new individual KRA PIN synchronously."""
        token = self._client.get_valid_token("pin_registration")
        url = f"{self._client.base_url}/v1/generate/pin"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        payload = {
            "TAXPAYERDETAILS": {
                "TaxpayerType": taxpayer_type,
                "IdentificationNumber": identification_number,
                "DateOfBirth": date_of_birth,
                "MobileNumber": mobile_number,
                "EmailAddress": email_address,
                "IsPinWithNoOblig": is_pin_with_no_obligation,
            }
        }

        try:
            response = self._client.client.post(url, headers=headers, json=payload)

            if response.status_code >= 500:
                raise TransientError(
                    f"KRA gateway server error: {response.status_code}"
                )

            response.raise_for_status()
            data = response.json()

            error_code = data.get("ErrorCode")
            if error_code is not None:
                error_msg = data.get("ErrorMessage")
                if str(error_code).strip() == "80002":
                    raise PinRegistrationValidationError(
                        error_msg or "Data Validation Error"
                    )
                raise GavaConnectError(f"API Error {error_code}: {error_msg}")

            validated = PinRegistrationResponse.model_validate(data)
            result = validated.result

            if result.status.upper() == "NOK":
                raise PinRegistrationValidationError(
                    result.message or "PIN registration failed"
                )

            return result

        except httpx.HTTPError as e:
            raise TransientError(f"Transport network failure: {str(e)}") from e
        except Exception as e:
            if isinstance(
                e, (PinRegistrationValidationError, TransientError, GavaConnectError)
            ):
                raise
            raise ValidationError(f"Response serialization failed: {str(e)}") from e
