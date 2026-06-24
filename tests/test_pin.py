import pytest
import respx
from httpx import Response

from gavaconnect import GavaConnect, GavaConnectSync
from gavaconnect.exceptions import AuthenticationError, InvalidPINError

# Configuration fixtures for testing
MOCK_CONFIG = {"consumer_key": "test_key", "consumer_secret": "test_secret"}
BASE_URL = "https://sbx.kra.go.ke"


# =====================================================================
# ASYNCHRONOUS TESTS
# =====================================================================


@pytest.mark.asyncio
@respx.mock
async def test_async_auth_success_and_caching():
    """Test that async token generation works and correctly caches the token."""
    client = GavaConnect(environment="sandbox", pin=MOCK_CONFIG)

    # Mock the authentication endpoint
    auth_route = respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(
            200, json={"access_token": "mock_token_123", "expires_in": 3600}
        )
    )

    # First call should hit the network
    token1 = await client.get_valid_token("pin")
    assert token1 == "mock_token_123"
    assert auth_route.call_count == 1
    assert client.token_cache["pin"]["access_token"] == "mock_token_123"

    # Second call should read instantly from the map cache
    token2 = await client.get_valid_token("pin")
    assert token2 == "mock_token_123"
    assert auth_route.call_count == 1  # Network call count shouldn't increase

    await client.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_async_auth_401_raises_authentication_error():
    """Test that a 401 returns a structural AuthenticationError with KRA message."""
    client = GavaConnect(environment="sandbox", pin=MOCK_CONFIG)

    respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(
            401, json={"errorMessage": "Client credentials are invalid"}
        )
    )

    with pytest.raises(AuthenticationError) as exc_info:
        await client.get_valid_token("pin")

    assert "Auth failed: Client credentials are invalid" in str(exc_info.value)
    await client.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_async_pin_check_success():
    """Test full async lifecycle for a successful PIN validation."""
    client = GavaConnect(environment="sandbox", pin=MOCK_CONFIG)

    # Mock Auth Route
    respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(
            200, json={"access_token": "valid_token", "expires_in": 3600}
        )
    )

    # Mock PIN Checker Route
    mock_payload = {
        "ResponseCode": "23000",
        "Message": "Valid PIN",
        "Status": "OK",
        "PINDATA": {
            "KRAPIN": "P318295670X",
            "TypeOfTaxpayer": "Non Individual",
            "Name": "EROCK ENTERPRISES LTD",
            "StatusOfPIN": "Active",
        },
    }
    respx.post(f"{BASE_URL}/checker/v1/pinbypin").mock(
        return_value=Response(200, json=mock_payload)
    )

    pin_result = await client.pin.check("P318295670X")

    assert pin_result.kra_pin == "P318295670X"
    assert pin_result.taxpayer_name == "EROCK ENTERPRISES LTD"
    assert pin_result.taxpayer_type == "Non Individual"
    assert pin_result.is_active is True

    await client.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_async_pin_check_invalid_error():
    """Test that an invalid PIN error code (19005) raises an InvalidPINError."""
    client = GavaConnect(environment="sandbox", pin=MOCK_CONFIG)

    respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(200, json={"access_token": "valid_token"})
    )

    mock_error_payload = {
        "ResponseCode": "19005",
        "Status": "NOK",
        "Message": "Invalid PIN",
    }
    respx.post(f"{BASE_URL}/checker/v1/pinbypin").mock(
        return_value=Response(200, json=mock_error_payload)
    )

    with pytest.raises(InvalidPINError) as exc_info:
        await client.pin.check("INVALID_PIN")

    assert "Invalid PIN" in str(exc_info.value)
    await client.aclose()


# =====================================================================
# SYNCHRONOUS TESTS
# =====================================================================


@respx.mock
def test_sync_auth_success_and_caching():
    """Test that the synchronous wrapper generates and caches tokens properly."""
    with GavaConnectSync(environment="sandbox", pin=MOCK_CONFIG) as client:
        auth_route = respx.get(f"{BASE_URL}/v1/token/generate").mock(
            return_value=Response(
                200, json={"access_token": "sync_token_123", "expires_in": 3600}
            )
        )

        token1 = client.get_valid_token("pin")
        assert token1 == "sync_token_123"
        assert auth_route.call_count == 1

        token2 = client.get_valid_token("pin")
        assert token2 == "sync_token_123"
        assert auth_route.call_count == 1


@respx.mock
def test_sync_pin_check_success():
    """Test full sync lifecycle for validation success."""
    with GavaConnectSync(environment="sandbox", pin=MOCK_CONFIG) as client:
        respx.get(f"{BASE_URL}/v1/token/generate").mock(
            return_value=Response(
                200, json={"access_token": "sync_token", "expires_in": 3600}
            )
        )

        mock_payload = {
            "ResponseCode": "23000",
            "Message": "Valid PIN",
            "Status": "OK",
            "PINDATA": {
                "KRAPIN": "A744610021G",
                "TypeOfTaxpayer": "Individual",
                "Name": "ERICK GAVACONNECT",
                "StatusOfPIN": "Active",
            },
        }
        respx.post(f"{BASE_URL}/checker/v1/pinbypin").mock(
            return_value=Response(200, json=mock_payload)
        )

        pin_result = client.pin.check("A744610021G")
        assert pin_result.taxpayer_name == "ERICK GAVACONNECT"
        assert pin_result.taxpayer_type == "Individual"
        assert pin_result.is_active is True
