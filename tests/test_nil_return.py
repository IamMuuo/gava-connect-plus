import pytest
import respx
from httpx import Response

from gavaconnect import GavaConnect, GavaConnectSync
from gavaconnect.exceptions import NilReturnValidationError

MOCK_CONFIG = {"consumer_key": "test_key", "consumer_secret": "test_secret"}
BASE_URL = "https://sbx.kra.go.ke"


@pytest.mark.asyncio
@respx.mock
async def test_async_nil_return_file_success():
    """Test successful async filing of a NIL return."""
    client = GavaConnect(environment="sandbox", nil_return=MOCK_CONFIG)

    respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(
            200, json={"access_token": "valid_nil_return_token", "expires_in": 3600}
        )
    )

    mock_success = {
        "RESPONSE": {
            "ResponseCode": " 82000",
            "Message": " Successfully Filled NIL Return ",
            "Status": "OK",
            "AckNumber": " KRAKBU1456050925 ",
        }
    }
    respx.post(f"{BASE_URL}/dtd/return/v1/nil").mock(
        return_value=Response(200, json=mock_success)
    )

    result = await client.nil_return.file("A521040203F", "1", "12", "2016")
    assert result.response_code == "82000"
    assert result.status == "OK"
    assert result.ack_number == "KRAKBU1456050925"
    await client.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_async_nil_return_file_validation_error():
    """Test that error code 82002 correctly triggers a NilReturnValidationError."""
    client = GavaConnect(environment="sandbox", nil_return=MOCK_CONFIG)

    respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(200, json={"access_token": "valid_nil_return_token"})
    )

    mock_error = {
        "requestId": "83f2-4b48-bdf5-4c7e1a67dbcb39076",
        "ErrorCode": "82002",
        "ErrorMessage": "Data Validation Error",
    }
    respx.post(f"{BASE_URL}/dtd/return/v1/nil").mock(
        return_value=Response(200, json=mock_error)
    )

    with pytest.raises(NilReturnValidationError) as exc_info:
        await client.nil_return.file("BADPIN0000A", "1", "12", "2016")

    assert "Data Validation Error" in str(exc_info.value)
    await client.aclose()


@respx.mock
def test_sync_nil_return_file_success():
    """Test successful synchronous filing of a NIL return."""
    with GavaConnectSync(environment="sandbox", nil_return=MOCK_CONFIG) as client:
        respx.get(f"{BASE_URL}/v1/token/generate").mock(
            return_value=Response(
                200,
                json={"access_token": "valid_nil_return_token", "expires_in": 3600},
            )
        )

        mock_success = {
            "RESPONSE": {
                "ResponseCode": "82000",
                "Message": "Successfully Filled NIL Return",
                "Status": "OK",
                "AckNumber": "KRAKBU1456050925",
            }
        }
        respx.post(f"{BASE_URL}/dtd/return/v1/nil").mock(
            return_value=Response(200, json=mock_success)
        )

        result = client.nil_return.file("A521040203F", "1", "12", "2016")
        assert result.ack_number == "KRAKBU1456050925"
