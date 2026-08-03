import pytest
import respx
from httpx import Response

from gavaconnect import GavaConnect, GavaConnectSync
from gavaconnect.exceptions import ExemptionNotFoundError, InvalidExemptionPINError

MOCK_CONFIG = {"consumer_key": "test_key", "consumer_secret": "test_secret"}
BASE_URL = "https://sbx.kra.go.ke"


@pytest.mark.asyncio
@respx.mock
async def test_async_exemption_check_success():
    """Test successful async exemption certificate check."""
    client = GavaConnect(environment="sandbox", exemption=MOCK_CONFIG)

    respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(
            200, json={"access_token": "valid_exemption_token", "expires_in": 3600}
        )
    )

    mock_success = {
        "response_message": "valid Exemption Certificate",
        "response_code": "200",
        "status_code": None,
        "cert_no": "KRAPWD0202050924",
        "cert_expiry_date": "2029-08-31 14:10:16.485",
        "cert_eff_date": "2024-09-01 00:00:00.0",
        "cert_issue_date": 1726830616479,
    }
    respx.post(f"{BASE_URL}/checker/v1/itexemption").mock(
        return_value=Response(200, json=mock_success)
    )

    result = await client.exemption.check("A352100031R")
    assert result.is_exempt is True
    assert result.cert_no == "KRAPWD0202050924"
    assert result.cert_expiry_date == "2029-08-31 14:10:16.485"
    await client.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_async_exemption_check_invalid_pin_error():
    """Test that response code 600 correctly triggers an InvalidExemptionPINError."""
    client = GavaConnect(environment="sandbox", exemption=MOCK_CONFIG)

    respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(200, json={"access_token": "valid_exemption_token"})
    )

    mock_error = {
        "response_message": "Invalid KRA PIN",
        "response_code": "600",
    }
    respx.post(f"{BASE_URL}/checker/v1/itexemption").mock(
        return_value=Response(200, json=mock_error)
    )

    with pytest.raises(InvalidExemptionPINError) as exc_info:
        await client.exemption.check("BADPIN0000A")

    assert "Invalid KRA PIN" in str(exc_info.value)
    await client.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_async_exemption_check_not_found_error():
    """Test that response code 900 correctly triggers an ExemptionNotFoundError."""
    client = GavaConnect(environment="sandbox", exemption=MOCK_CONFIG)

    respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(200, json={"access_token": "valid_exemption_token"})
    )

    mock_error = {
        "response_message": "invalid Exemption Certificate",
        "response_code": "900",
    }
    respx.post(f"{BASE_URL}/checker/v1/itexemption").mock(
        return_value=Response(200, json=mock_error)
    )

    with pytest.raises(ExemptionNotFoundError) as exc_info:
        await client.exemption.check("A501115280R")

    assert "invalid Exemption Certificate" in str(exc_info.value)
    await client.aclose()


@respx.mock
def test_sync_exemption_check_success():
    """Test successful synchronous exemption certificate check."""
    with GavaConnectSync(environment="sandbox", exemption=MOCK_CONFIG) as client:
        respx.get(f"{BASE_URL}/v1/token/generate").mock(
            return_value=Response(
                200,
                json={"access_token": "valid_exemption_token", "expires_in": 3600},
            )
        )

        mock_success = {
            "response_message": "valid Exemption Certificate",
            "response_code": "200",
            "status_code": None,
            "cert_no": "KRAPWD0202050924",
            "cert_expiry_date": "2029-08-31 14:10:16.485",
            "cert_eff_date": "2024-09-01 00:00:00.0",
            "cert_issue_date": 1726830616479,
        }
        respx.post(f"{BASE_URL}/checker/v1/itexemption").mock(
            return_value=Response(200, json=mock_success)
        )

        result = client.exemption.check("A160804302G")
        assert result.is_exempt is True
        assert result.cert_no == "KRAPWD0202050924"
