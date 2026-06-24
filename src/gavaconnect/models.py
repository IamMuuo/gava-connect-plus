from decimal import Decimal
from typing import Any, List, Optional
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


class InvoiceDetails(BaseModel):
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
    trader_system_invoice_number: str = Field(alias="traderSystemInvoiceNumber")

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


class IdLookupResponse(BaseModel):
    taxpayer_pin: str = Field(alias="TaxpayerPIN")
    taxpayer_name: str = Field(alias="TaxpayerName")
