from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class AnalyticsRequest(BaseModel):
    """Request schema for analytics endpoints."""
    target_currency: Optional[str] = Field(
        None, 
        min_length=3, 
        max_length=3, 
        description="Currency code for conversion (3 characters, e.g., USD, EUR, GBP). Defaults to system default currency if not provided."
    )
    customer_id: Optional[int] = Field(
        None,
        gt=0,
        description="Filter analytics by specific customer ID"
    )
    start_date: Optional[date] = Field(
        None,
        description="Start date for filtering invoices (inclusive). Format: YYYY-MM-DD (e.g., 2024-01-01)"
    )
    end_date: Optional[date] = Field(
        None,
        description="End date for filtering invoices (inclusive). Format: YYYY-MM-DD (e.g., 2024-12-31)"
    )


class TotalRevenueResponse(BaseModel):
    """Response schema for total revenue analytics."""
    total_revenue: float = Field(..., description="Total revenue in the target currency")
    currency: str = Field(..., description="Currency code of the total revenue")
    invoice_count: int = Field(..., description="Number of invoices included in calculation")
    start_date: Optional[date] = Field(None, description="Start date filter applied")
    end_date: Optional[date] = Field(None, description="End date filter applied")
    customer_id: Optional[int] = Field(None, description="Customer ID filter applied")


class AverageInvoiceResponse(BaseModel):
    """Response schema for average invoice size analytics."""
    average_invoice_size: float = Field(..., description="Average invoice size in the target currency")
    currency: str = Field(..., description="Currency code of the average")
    invoice_count: int = Field(..., description="Number of invoices included in calculation")
    start_date: Optional[date] = Field(None, description="Start date filter applied")
    end_date: Optional[date] = Field(None, description="End date filter applied")
    customer_id: Optional[int] = Field(None, description="Customer ID filter applied")

