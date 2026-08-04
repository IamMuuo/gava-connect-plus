import pytest
import respx
from httpx import Response

from gavaconnect import GavaConnect, GavaConnectSync
from gavaconnect.exceptions import PinRegistrationValidationError

MOCK_CONFIG = {"consumer_key": "test_key", "consumer_secret": "test_secret"}
BASE_URL = "https://sbx.kra.go.ke"


@pytest.mark.asyncio
@respx.mock
async def test_async_pin_registration_success():
    """Test successful async registration of an individual KRA PIN."""
    client = GavaConnect(environment="sandbox", pin_registration=MOCK_CONFIG)

    respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(
            200,
            json={"access_token": "valid_pin_registration_token", "expires_in": 3600},
        )
    )

    mock_success = {
        "RESPONSE": {
            "ResponseCode": "80000",
            "Message": "Successfully Generated PIN",
            "Status": "OK",
            "PIN": "A000000000B",
        }
    }
    respx.post(f"{BASE_URL}/v1/generate/pin").mock(
        return_value=Response(200, json=mock_success)
    )

    result = await client.pin_registration.register(
        taxpayer_type="KE",
        identification_number="90987908",
        date_of_birth="01/01/1990",
        mobile_number="0700000000",
        email_address="dummy@email.com",
        is_pin_with_no_obligation="Yes",
    )
    assert result.pin == "A000000000B"
    assert result.status == "OK"
    await client.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_async_pin_registration_validation_error():
    """Test that error code 80002 correctly triggers a PinRegistrationValidationError."""
    client = GavaConnect(environment="sandbox", pin_registration=MOCK_CONFIG)

    respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(
            200, json={"access_token": "valid_pin_registration_token"}
        )
    )

    mock_error = {
        "RequestId": "77d0f584-1428-4d5e-9efd-3f5642a9302267225",
        "ErrorCode": "80002",
        "ErrorMessage": "Data Validation Error(email address already used)",
    }
    respx.post(f"{BASE_URL}/v1/generate/pin").mock(
        return_value=Response(200, json=mock_error)
    )

    with pytest.raises(PinRegistrationValidationError) as exc_info:
        await client.pin_registration.register(
            taxpayer_type="KE",
            identification_number="90987908",
            date_of_birth="01/01/1990",
            mobile_number="0700000000",
            email_address="dummy@email.com",
        )

    assert "Data Validation Error" in str(exc_info.value)
    await client.aclose()


@respx.mock
def test_sync_pin_registration_success():
    """Test successful synchronous registration of an individual KRA PIN."""
    with GavaConnectSync(
        environment="sandbox", pin_registration=MOCK_CONFIG
    ) as client:
        respx.get(f"{BASE_URL}/v1/token/generate").mock(
            return_value=Response(
                200,
                json={
                    "access_token": "valid_pin_registration_token",
                    "expires_in": 3600,
                },
            )
        )

        mock_success = {
            "RESPONSE": {
                "ResponseCode": "80000",
                "Message": "Successfully Generated PIN",
                "Status": "OK",
                "PIN": "A521040203F",
            }
        }
        respx.post(f"{BASE_URL}/v1/generate/pin").mock(
            return_value=Response(200, json=mock_success)
        )

        result = client.pin_registration.register(
            taxpayer_type="KE",
            identification_number="12345678",
            date_of_birth="15/06/1985",
            mobile_number="0711000000",
            email_address="sync@email.com",
        )
        assert result.pin == "A521040203F"
