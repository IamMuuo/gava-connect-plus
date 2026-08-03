import pytest
import respx
from httpx import Response

from gavaconnect import GavaConnect, GavaConnectSync
from gavaconnect.exceptions import InvalidExciseLicenseError

MOCK_CONFIG = {"consumer_key": "test_key", "consumer_secret": "test_secret"}
BASE_URL = "https://sbx.kra.go.ke"


@pytest.mark.asyncio
@respx.mock
async def test_async_excise_license_check_success():
    """Test successful async validation of an Excise License Certificate Number."""
    client = GavaConnect(environment="sandbox", excise_license=MOCK_CONFIG)

    respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(
            200, json={"access_token": "valid_excise_token", "expires_in": 3600}
        )
    )

    mock_success = {
        "Status": "OK",
        "ResponseCode": "80000",
        "Message": "Valid PIN Number",
        "ExciseLicenseDATA": {
            "Status": "Approved",
            "ClassOfGoods": "BW",
            "TaxpayerName": "XECUT 051621TEST",
            "DateOfIssue": "16/04/2020",
            "ExciseLicenceNo": "KRAHQS0019742020",
            "PINNo": "P051621738A",
        },
    }
    respx.post(f"{BASE_URL}/checker/v1/ExciseLicenseByNum").mock(
        return_value=Response(200, json=mock_success)
    )

    result = await client.excise_license.check_by_number("QK0810SR8A00092H")
    assert result.is_approved is True
    assert result.taxpayer_name == "XECUT 051621TEST"
    assert result.pin_no == "P051621738A"
    await client.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_async_excise_license_check_invalid_error():
    """Test that response code 80002 correctly triggers an InvalidExciseLicenseError."""
    client = GavaConnect(environment="sandbox", excise_license=MOCK_CONFIG)

    respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(200, json={"access_token": "valid_excise_token"})
    )

    mock_error = {
        "Status": "NOK",
        "ResponseCode": "80002",
        "Message": "Invalid Excise License Number",
    }
    respx.post(f"{BASE_URL}/checker/v1/ExciseLicenseByNum").mock(
        return_value=Response(200, json=mock_error)
    )

    with pytest.raises(InvalidExciseLicenseError) as exc_info:
        await client.excise_license.check_by_number("BADLICENCE0000")

    assert "Invalid Excise License Number" in str(exc_info.value)
    await client.aclose()


@respx.mock
def test_sync_excise_license_check_success():
    """Test successful synchronous validation of an Excise License Certificate Number."""
    with GavaConnectSync(environment="sandbox", excise_license=MOCK_CONFIG) as client:
        respx.get(f"{BASE_URL}/v1/token/generate").mock(
            return_value=Response(
                200, json={"access_token": "valid_excise_token", "expires_in": 3600}
            )
        )

        mock_success = {
            "Status": "OK",
            "ResponseCode": "80000",
            "Message": "Valid PIN Number",
            "ExciseLicenseDATA": {
                "Status": "Approved",
                "ClassOfGoods": "BW",
                "TaxpayerName": "XECUT 051621TEST",
                "DateOfIssue": "16/04/2020",
                "ExciseLicenceNo": "012900SKQ8H1A2R0",
                "PINNo": "P051621738A",
            },
        }
        respx.post(f"{BASE_URL}/checker/v1/ExciseLicenseByNum").mock(
            return_value=Response(200, json=mock_success)
        )

        result = client.excise_license.check_by_number("012900SKQ8H1A2R0")
        assert result.is_approved is True
        assert result.class_of_goods == "BW"
