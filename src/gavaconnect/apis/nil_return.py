from typing import TYPE_CHECKING
import httpx

from gavaconnect.exceptions import (
    GavaConnectError,
    NilReturnValidationError,
    TransientError,
    ValidationError,
)
from gavaconnect.models import NilReturnResponse, NilReturnResult, ObligationCode

if TYPE_CHECKING:
    from gavaconnect.async_client import GavaConnect
    from gavaconnect.sync_client import GavaConnectSync


class NilReturnAPI:
    """Asynchronous NIL Return Filing API Wrapper."""

    def __init__(self, client: "GavaConnect") -> None:
        self._client = client

    async def file(
        self, pin: str, obligation_code: ObligationCode, month: str, year: str
    ) -> NilReturnResult:
        """File a NIL return for a taxpayer with no taxable income in the period.

        Ref: https://sbx.kra.go.ke/dtd/return/v1/nil
        """
        token = await self._client.get_valid_token("nil_return")
        url = f"{self._client.base_url}/dtd/return/v1/nil"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        payload = {
            "TAXPAYERDETAILS": {
                "TaxpayerPIN": pin,
                "ObligationCode": obligation_code,
                "Month": month,
                "Year": year,
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
                if str(error_code).strip() == "82002":
                    raise NilReturnValidationError(
                        error_msg or "Data Validation Error"
                    )
                raise GavaConnectError(f"API Error {error_code}: {error_msg}")

            validated = NilReturnResponse.model_validate(data)
            result = validated.result

            if result.status.upper() == "NOK":
                raise NilReturnValidationError(
                    result.message or "NIL return filing failed"
                )

            return result

        except httpx.HTTPError as e:
            raise TransientError(f"Transport network failure: {str(e)}") from e
        except Exception as e:
            if isinstance(
                e, (NilReturnValidationError, TransientError, GavaConnectError)
            ):
                raise
            raise ValidationError(f"Response serialization failed: {str(e)}") from e


class SyncNilReturnAPI:
    """Synchronous NIL Return Filing API Wrapper."""

    def __init__(self, client: "GavaConnectSync") -> None:
        self._client = client

    def file(
        self, pin: str, obligation_code: ObligationCode, month: str, year: str
    ) -> NilReturnResult:
        """File a NIL return for a taxpayer with no taxable income in the period synchronously."""
        token = self._client.get_valid_token("nil_return")
        url = f"{self._client.base_url}/dtd/return/v1/nil"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        payload = {
            "TAXPAYERDETAILS": {
                "TaxpayerPIN": pin,
                "ObligationCode": obligation_code,
                "Month": month,
                "Year": year,
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
                if str(error_code).strip() == "82002":
                    raise NilReturnValidationError(
                        error_msg or "Data Validation Error"
                    )
                raise GavaConnectError(f"API Error {error_code}: {error_msg}")

            validated = NilReturnResponse.model_validate(data)
            result = validated.result

            if result.status.upper() == "NOK":
                raise NilReturnValidationError(
                    result.message or "NIL return filing failed"
                )

            return result

        except httpx.HTTPError as e:
            raise TransientError(f"Transport network failure: {str(e)}") from e
        except Exception as e:
            if isinstance(
                e, (NilReturnValidationError, TransientError, GavaConnectError)
            ):
                raise
            raise ValidationError(f"Response serialization failed: {str(e)}") from e
