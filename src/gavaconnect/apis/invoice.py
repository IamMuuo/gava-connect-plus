from datetime import date
from typing import TYPE_CHECKING
import httpx

from gavaconnect.exceptions import (
    GavaConnectError,
    InvoiceNotFoundError,
    TransientError,
    ValidationError,
)
from gavaconnect.models import InvoiceDetails, InvoiceResponse

if TYPE_CHECKING:
    from gavaconnect.async_client import GavaConnect
    from gavaconnect.sync_client import GavaConnectSync


class InvoiceAPI:
    """Asynchronous Invoice Checker API Wrapper."""

    def __init__(self, client: "GavaConnect") -> None:
        self._client = client

    async def get(self, invoice_number: str, invoice_date: date) -> InvoiceDetails:
        """Look up a KRA eTIMS invoice by invoice number and date.

        Ref: https://sbx.kra.go.ke/checker/v1/invoice
        """
        token = await self._client.get_valid_token("invoice")
        url = f"{self._client.base_url}/checker/v1/invoice"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        # Internal YYYY-MM-DD date transformation
        payload = {
            "invoiceNumber": invoice_number,
            "invoiceDate": invoice_date.strftime("%Y-%m-%d"),
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

            resp_code = data.get("responseCode")

            if resp_code == 40001:
                raise InvoiceNotFoundError(
                    data.get("responseDesc", "Invoice not found.")
                )
            elif resp_code in (40005, 50000):
                raise TransientError(
                    data.get("responseDesc", "KRA internal transient error.")
                )
            elif resp_code != 40000:
                raise GavaConnectError(f"Unexpected API error code: {resp_code}")

            validated = InvoiceResponse.model_validate(data)
            if not validated.invoice_details:
                raise ValidationError(
                    "Response marked successful but omitted invoiceDetails payload."
                )

            return validated.invoice_details

        except httpx.HTTPError as e:
            raise TransientError(f"Transport network failure: {str(e)}") from e
        except Exception as e:
            if isinstance(e, (InvoiceNotFoundError, TransientError, GavaConnectError)):
                raise
            raise ValidationError(f"Response serialization failed: {str(e)}") from e


class SyncInvoiceAPI:
    """Synchronous Invoice Checker API Wrapper."""

    def __init__(self, client: "GavaConnectSync") -> None:
        self._client = client

    def get(self, invoice_number: str, invoice_date: date) -> InvoiceDetails:
        """Look up a KRA eTIMS invoice synchronously."""
        token = self._client.get_valid_token("invoice")
        url = f"{self._client.base_url}/checker/v1/invoice"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        payload = {
            "invoiceNumber": invoice_number,
            "invoiceDate": invoice_date.strftime("%Y-%m-%d"),
        }

        try:
            response = self._client.client.post(url, headers=headers, json=payload)

            if response.status_code >= 500:
                raise TransientError(
                    f"KRA gateway server error: {response.status_code}"
                )

            response.raise_for_status()
            data = response.json()

            resp_code = data.get("responseCode")

            if resp_code == 40001:
                raise InvoiceNotFoundError(
                    data.get("responseDesc", "Invoice not found.")
                )
            elif resp_code in (40005, 50000):
                raise TransientError(
                    data.get("responseDesc", "KRA internal transient error.")
                )
            elif resp_code != 40000:
                raise GavaConnectError(f"Unexpected API error code: {resp_code}")

            validated = InvoiceResponse.model_validate(data)
            if not validated.invoice_details:
                raise ValidationError(
                    "Response marked successful but omitted invoiceDetails payload."
                )

            return validated.invoice_details

        except httpx.HTTPError as e:
            raise TransientError(f"Transport network failure: {str(e)}") from e
        except Exception as e:
            if isinstance(e, (InvoiceNotFoundError, TransientError, GavaConnectError)):
                raise
            raise ValidationError(f"Response serialization failed: {str(e)}") from e
