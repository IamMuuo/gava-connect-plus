import pytest
import respx
from httpx import Response

from gavaconnect import GavaConnect, GavaConnectSync
from gavaconnect.exceptions import (
    TaxpayerNotFoundError,
    TransientError,
    ValidationError,
)

MOCK_CONFIG = {"consumer_key": "test_key", "consumer_secret": "test_secret"}
BASE_URL = "https://sbx.kra.go.ke"


@pytest.mark.asyncio
@respx.mock
async def test_async_pin_lookup_success():
    """Test full async lifecycle for resolving a KRA PIN successfully."""
    client = GavaConnect(environment="sandbox", pin_lookup=MOCK_CONFIG)

    # Intercept OAuth token lifecycle request
    respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(
            200, json={"access_token": "pin_lookup_token", "expires_in": 3600}
        )
    )

    # Intercept KRA PIN resolution success payload
    mock_payload = {
        "TaxpayerPIN": "A000000000I",
        "TaxpayerName": "YAMAS12 TEST OMINI01",
    }
    respx.post(f"{BASE_URL}/checker/v1/pin").mock(
        return_value=Response(200, json=mock_payload)
    )

    result = await client.pin_lookup.by_id(taxpayer_id="100000000", taxpayer_type="KE")

    assert result.taxpayer_pin == "A000000000I"
    assert result.taxpayer_name == "YAMAS12 TEST OMINI01"

    await client.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_async_pin_lookup_not_found():
    """Test that KRA error code 30002 raises TaxpayerNotFoundError asynchronously."""
    client = GavaConnect(environment="sandbox", pin_lookup=MOCK_CONFIG)

    respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(200, json={"access_token": "pin_lookup_token"})
    )

    respx.post(f"{BASE_URL}/checker/v1/pin").mock(
        return_value=Response(
            200,
            json={
                "RequestId": "526e10fa-3db9-4a3b-96f1-7c04b2e2252b1302",
                "ErrorCode": "30002",
                "ErrorMessage": "Invalid ID",
            },
        )
    )

    with pytest.raises(TaxpayerNotFoundError):
        await client.pin_lookup.by_id(taxpayer_id="41789723", taxpayer_type="KE")

    await client.aclose()


@respx.mock
def test_sync_pin_lookup_validation_error():
    """Test that KRA code 400 maps directly to a ValidationError synchronously."""
    with GavaConnectSync(environment="sandbox", pin_lookup=MOCK_CONFIG) as client:
        respx.get(f"{BASE_URL}/v1/token/generate").mock(
            return_value=Response(200, json={"access_token": "sync_pin_token"})
        )

        respx.post(f"{BASE_URL}/checker/v1/pin").mock(
            return_value=Response(
                200,
                json={
                    "requestId": "526e10fa-3db9-4a3b-96f1-7c04b2e2252b1303",
                    "errorCode": "400",
                    "errorMessage": "Missing mandatory parameter: TaxpayerID.",
                },
            )
        )

        with pytest.raises(ValidationError):
            client.pin_lookup.by_id(taxpayer_id="", taxpayer_type="COMP")


@respx.mock
def test_sync_pin_lookup_gateway_transient_error():
    """Test that a raw HTTP 502/500 from the KRA gateway drops into a TransientError."""
    with GavaConnectSync(environment="sandbox", pin_lookup=MOCK_CONFIG) as client:
        respx.get(f"{BASE_URL}/v1/token/generate").mock(
            return_value=Response(200, json={"access_token": "sync_pin_token"})
        )

        # Mock direct network proxy drops / server issues
        respx.post(f"{BASE_URL}/checker/v1/pin").mock(
            return_value=Response(502, text="Bad Gateway")
        )

        with pytest.raises(TransientError):
            client.pin_lookup.by_id(taxpayer_id="100000000", taxpayer_type="NKE")
