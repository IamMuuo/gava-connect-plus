from datetime import date
from decimal import Decimal
import pytest
import respx
from httpx import Response

from gavaconnect import GavaConnect, GavaConnectSync
from gavaconnect.exceptions import InvoiceNotFoundError, TransientError

MOCK_CONFIG = {"consumer_key": "test_key", "consumer_secret": "test_secret"}
BASE_URL = "https://sbx.kra.go.ke"


@pytest.mark.asyncio
@respx.mock
async def test_async_invoice_get_success():
    """Test full async lifecycle for fetching invoice details successfully."""
    client = GavaConnect(environment="sandbox", invoice=MOCK_CONFIG)

    # Mock Auth
    respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(
            200, json={"access_token": "invoice_token", "expires_in": 3600}
        )
    )

    # Mock success payload
    mock_payload = {
        "responseCode": 40000,
        "responseDesc": "Invoice details retrieved successfully.",
        "status": "OK",
        "invoiceDetails": {
            "salesDate": "2025-10-26",
            "transmissionDate": "2025-10-26T16:51:29",
            "invoiceDate": "2025-10-26T16:50:24",
            "totalItemCount": 1,
            "supplierPIN": "P051xxx23G",
            "supplierName": "Avas Limit",
            "deviceSerialNumber": "KRAMW079757",
            "customerPin": None,
            "customerName": None,
            "controlUnitInvoiceNumber": "0040717",
            "traderSystemInvoiceNumber": "0066330856",
            "totalInvoiceAmount": 1764.0,
            "totalTaxableAmount": 1520.69,
            "totalTaxAmount": 243.31,
            "exemptionCertificateNo": None,
            "totalDiscountAmount": 0.0,
            "itemDetails": [],
        },
    }
    respx.post(f"{BASE_URL}/checker/v1/invoice").mock(
        return_value=Response(200, json=mock_payload)
    )

    invoice = await client.invoice.get(
        invoice_number="KRACU0100058659/5134", invoice_date=date(2024, 8, 18)
    )

    assert invoice.supplier_pin == "P051xxx23G"
    assert invoice.supplier_name == "Avas Limit"

    # Asserting target strict type translation rules
    assert isinstance(invoice.total_invoice_amount, Decimal)
    assert invoice.total_invoice_amount == Decimal("1764.0")
    assert invoice.total_taxable_amount == Decimal("1520.69")

    await client.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_async_invoice_not_found():
    """Test that error code 40001 throws InvoiceNotFoundError."""
    client = GavaConnect(environment="sandbox", invoice=MOCK_CONFIG)

    respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(200, json={"access_token": "invoice_token"})
    )

    respx.post(f"{BASE_URL}/checker/v1/invoice").mock(
        return_value=Response(
            200,
            json={
                "responseCode": 40001,
                "responseDesc": "Invoice not found.",
                "status": "ERROR",
            },
        )
    )

    with pytest.raises(InvoiceNotFoundError):
        await client.invoice.get("MISSING", date(2024, 8, 18))

    await client.aclose()


@respx.mock
def test_sync_invoice_transient_error():
    """Test that a 40005 code maps to a retryable TransientError synchronously."""
    with GavaConnectSync(environment="sandbox", invoice=MOCK_CONFIG) as client:
        respx.get(f"{BASE_URL}/v1/token/generate").mock(
            return_value=Response(200, json={"access_token": "sync_token"})
        )

        respx.post(f"{BASE_URL}/checker/v1/invoice").mock(
            return_value=Response(
                200,
                json={
                    "responseCode": 40005,
                    "responseDesc": "Unable to process request - Try Again",
                    "status": "ERROR",
                },
            )
        )

        with pytest.raises(TransientError):
            client.invoice.get("TRY_AGAIN_ID", date(2024, 8, 18))
