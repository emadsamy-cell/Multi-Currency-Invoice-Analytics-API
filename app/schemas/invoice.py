from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class InvoiceBase(BaseModel):
    customer_id: int = Field(..., gt=0, description="Customer ID (required)")
    amount: float = Field(..., gt=0, description="Invoice amount (must be positive)")
    currency: str = Field(..., min_length=3, max_length=3, description="Currency code (3 characters, e.g., USD, EUR, GBP)")


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0, description="Invoice amount (must be positive)")
    currency: Optional[str] = Field(None, min_length=3, max_length=3, description="Currency code (3 characters)")


class InvoiceResponse(InvoiceBase):
    id: int
    amount_in_default_currency: Optional[float] = None
    exchange_rate: Optional[float] = None
    default_currency: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

