import pytest
import respx
from httpx import Response

from gavaconnect import GavaConnect, GavaConnectSync
from gavaconnect.exceptions import InvalidObligationPINError

MOCK_CONFIG = {"consumer_key": "test_key", "consumer_secret": "test_secret"}
BASE_URL = "https://sbx.kra.go.ke"


@pytest.mark.asyncio
@respx.mock
async def test_async_obligation_fetch_success():
    """Test successful async extraction of taxpayer obligation details."""
    client = GavaConnect(environment="sandbox", obligation=MOCK_CONFIG)

    respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(
            200, json={"access_token": "valid_obligation_token", "expires_in": 3600}
        )
    )

    mock_success = {
        "ResponseCode": "20000",
        "ResponseMsg": "Valid KRA Pin",
        "Status": "OK",
        "ObligationsList": [
            {
                "obligationId": "2",
                "obligationName": "Income Tax - Resident Individual",
                "obligationType": "NRM",
            },
            {
                "obligationId": "22",
                "obligationName": "Advance Tax",
                "obligationType": "SPL",
            },
        ],
    }
    respx.post(f"{BASE_URL}/dtd/checker/v1/obligation").mock(
        return_value=Response(200, json=mock_success)
    )

    obligations = await client.obligation.fetch("A744610021G")
    assert len(obligations) == 2
    assert obligations[0].obligation_id == "2"
    assert obligations[0].obligation_name == "Income Tax - Resident Individual"
    assert obligations[1].obligation_type == "SPL"
    await client.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_async_obligation_fetch_invalid_pin_error():
    """Test that response code 20001 correctly triggers an InvalidObligationPINError."""
    client = GavaConnect(environment="sandbox", obligation=MOCK_CONFIG)

    respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(200, json={"access_token": "valid_obligation_token"})
    )

    mock_error = {
        "ResponseCode": "20001",
        "ResponseMsg": "Invalid KRA Pin",
        "Status": "NOK",
    }
    respx.post(f"{BASE_URL}/dtd/checker/v1/obligation").mock(
        return_value=Response(200, json=mock_error)
    )

    with pytest.raises(InvalidObligationPINError) as exc_info:
        await client.obligation.fetch("WRONG_PIN")

    assert "Invalid KRA Pin" in str(exc_info.value)
    await client.aclose()


@respx.mock
def test_sync_obligation_fetch_success():
    """Test successful synchronous operation of the obligation fetcher interface."""
    with GavaConnectSync(environment="sandbox", obligation=MOCK_CONFIG) as client:
        respx.get(f"{BASE_URL}/v1/token/generate").mock(
            return_value=Response(
                200,
                json={"access_token": "valid_obligation_token", "expires_in": 3600},
            )
        )

        mock_success = {
            "ResponseCode": "20000",
            "ResponseMsg": "Valid KRA Pin",
            "Status": "OK",
            "ObligationsList": [
                {
                    "obligationId": "10",
                    "obligationName": "VAT on Services Imported",
                    "obligationType": "SPL",
                }
            ],
        }
        respx.post(f"{BASE_URL}/dtd/checker/v1/obligation").mock(
            return_value=Response(200, json=mock_success)
        )

        obligations = client.obligation.fetch("P318295670X")
        assert len(obligations) == 1
        assert obligations[0].obligation_name == "VAT on Services Imported"
