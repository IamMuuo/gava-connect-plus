from decimal import Decimal
from typing import Any, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


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


class InvoiceDetails(BaseModel):
    model_config = ConfigDict(
        json_encoders={
            Decimal: str,
        },
    )
    sales_date: str = Field(alias="salesDate")
    transmission_date: str = Field(alias="transmissionDate")
    invoice_date: str = Field(alias="invoiceDate")
    total_item_count: int = Field(alias="totalItemCount")
    supplier_pin: str = Field(alias="supplierPIN")
    supplier_name: str = Field(alias="supplierName")
    device_serial_number: str = Field(alias="deviceSerialNumber")
    customer_pin: Optional[str] = Field(None, alias="customerPin")
    customer_name: Optional[str] = Field(None, alias="customerName")
    control_unit_invoice_number: str = Field(alias="controlUnitInvoiceNumber")
    trader_system_invoice_number: Optional[str] = Field(
        alias="traderSystemInvoiceNumber"
    )

    # Enforcing Decimal for all monetary elements
    total_invoice_amount: Decimal = Field(alias="totalInvoiceAmount")
    total_taxable_amount: Decimal = Field(alias="totalTaxableAmount")
    total_tax_amount: Decimal = Field(alias="totalTaxAmount")
    exemption_certificate_no: Optional[str] = Field(
        None, alias="exemptionCertificateNo"
    )
    total_discount_amount: Decimal = Field(alias="totalDiscountAmount")

    # Keeping item details flexible since KRA docs supply an empty array fallback
    item_details: List[Any] = Field(alias="itemDetails")


class InvoiceResponse(BaseModel):
    response_code: int = Field(alias="responseCode")
    response_desc: str = Field(alias="responseDesc")
    status: str = Field(alias="status")
    invoice_details: Optional[InvoiceDetails] = Field(None, alias="invoiceDetails")


class StationData(BaseModel):
    kra_pin: str = Field(alias="kraPin")
    station_name: str = Field(alias="stationName")


class StationResponse(BaseModel):
    response_code: str = Field(alias="ResponseCode")
    message: str = Field(alias="Message")
    status: str = Field(alias="Status")
    station_data: StationData = Field(alias="STATIONDATA")


TaxpayerType = Literal["KE", "NKE", "NKENRB", "COMP"]


class PinLookupResponse(BaseModel):
    """Pydantic model validating KRA PIN Checker by ID responses."""

    taxpayer_pin: str = Field(..., alias="TaxpayerPIN")
    taxpayer_name: str = Field(..., alias="TaxpayerName")

    model_config = {
        "populate_by_name": True,
        "frozen": True,
    }


class ObligationData(BaseModel):
    obligation_id: str = Field(alias="obligationId")
    obligation_name: str = Field(alias="obligationName")
    obligation_type: str = Field(alias="obligationType")


class ObligationResponse(BaseModel):
    response_code: str = Field(alias="ResponseCode")
    message: str = Field(alias="ResponseMsg")
    status: str = Field(alias="Status")
    obligations_list: List[ObligationData] = Field(
        default_factory=list, alias="ObligationsList"
    )


ObligationCode = Literal["1", "2", "3", "4", "5", "6", "7", "8"]


class NilReturnResult(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    response_code: str = Field(alias="ResponseCode")
    message: str = Field(alias="Message")
    status: str = Field(alias="Status")
    ack_number: str = Field(alias="AckNumber")


class NilReturnResponse(BaseModel):
    result: NilReturnResult = Field(alias="RESPONSE")


class ExemptionData(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    response_code: str = Field(alias="response_code")
    response_message: str = Field(alias="response_message")
    status_code: Optional[str] = Field(None, alias="status_code")
    cert_no: Optional[str] = Field(None, alias="cert_no")
    cert_expiry_date: Optional[str] = Field(None, alias="cert_expiry_date")
    cert_eff_date: Optional[str] = Field(None, alias="cert_eff_date")
    cert_issue_date: Optional[int] = Field(None, alias="cert_issue_date")

    @property
    def is_exempt(self) -> bool:
        """Returns True if the taxpayer holds a valid Income Tax/VAT exemption certificate."""
        return self.response_code.strip() == "200"
