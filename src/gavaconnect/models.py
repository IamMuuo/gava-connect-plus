from pydantic import BaseModel, Field


class PinData(BaseModel):
    kra_pin: str = Field(alias="KRAPIN")
    type_of_taxpayer: str = Field(alias="TypeOfTaxpayer")
    name: str = Field(alias="Name")
    status_of_pin: str = Field(alias="StatusOfPIN")

    @property
    def is_active(self) -> bool:
        """Returns True if the taxpayer's KRA PIN status is Active."""
        return self.status_of_pin.strip().lower() == "active"

    @property
    def taxpayer_name(self) -> str:
        """Returns the legal registered name of the taxpayer."""
        return self.name

    @property
    def taxpayer_type(self) -> str:
        """Returns the classification type (Individual / Non Individual)."""
        return self.type_of_taxpayer


class PinResponse(BaseModel):
    response_code: str = Field(alias="ResponseCode")
    message: str = Field(alias="Message")
    status: str = Field(alias="Status")
    pin_data: PinData = Field(alias="PINDATA")
