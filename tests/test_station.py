import pytest
import respx
from httpx import Response

from gavaconnect import GavaConnect, GavaConnectSync
from gavaconnect.exceptions import InvalidStationPINError

MOCK_CONFIG = {"consumer_key": "test_key", "consumer_secret": "test_secret"}
BASE_URL = "https://sbx.kra.go.ke"


@pytest.mark.asyncio
@respx.mock
async def test_async_station_lookup_success():
    """Test successful async extraction of taxpayer station information."""
    # Changed configuration allocation from pin= to station=
    client = GavaConnect(environment="sandbox", station=MOCK_CONFIG)

    respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(
            200, json={"access_token": "valid_station_token", "expires_in": 3600}
        )
    )

    mock_success = {
        "ResponseCode": "84000",
        "Message": "Station Name is sent successfully",
        "Status": "OK",
        "STATIONDATA": {"kraPin": "A744610021G", "stationName": "West of Nairobi"},
    }
    respx.post(f"{BASE_URL}/dtd/checker/v1/station").mock(
        return_value=Response(200, json=mock_success)
    )

    station = await client.station.get("A744610021G")
    assert station.kra_pin == "A744610021G"
    assert station.station_name == "West of Nairobi"
    await client.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_async_station_lookup_invalid_pin_error():
    """Test that error code 84002 correctly triggers an InvalidStationPINError."""
    # Changed configuration allocation from pin= to station=
    client = GavaConnect(environment="sandbox", station=MOCK_CONFIG)

    respx.get(f"{BASE_URL}/v1/token/generate").mock(
        return_value=Response(200, json={"access_token": "valid_station_token"})
    )

    mock_error = {
        "ResponseCode": "84002",
        "Message": "Inactive / Wrong PIN",
        "Status": "ERROR",
    }
    respx.post(f"{BASE_URL}/dtd/checker/v1/station").mock(
        return_value=Response(200, json=mock_error)
    )

    with pytest.raises(InvalidStationPINError) as exc_info:
        await client.station.get("WRONG_PIN")

    assert "Inactive / Wrong PIN" in str(exc_info.value)
    await client.aclose()


@respx.mock
def test_sync_station_lookup_success():
    """Test successful synchronous operation of the station checker interface."""
    # Changed configuration allocation from pin= to station=
    with GavaConnectSync(environment="sandbox", station=MOCK_CONFIG) as client:
        respx.get(f"{BASE_URL}/v1/token/generate").mock(
            return_value=Response(
                200, json={"access_token": "valid_station_token", "expires_in": 3600}
            )
        )

        mock_success = {
            "ResponseCode": "84000",
            "Message": "Station Name is sent successfully",
            "Status": "OK",
            "STATIONDATA": {"kraPin": "P318295670X", "stationName": "Mombasa Port"},
        }
        respx.post(f"{BASE_URL}/dtd/checker/v1/station").mock(
            return_value=Response(200, json=mock_success)
        )

        station = client.station.get("P318295670X")
        assert station.station_name == "Mombasa Port"
