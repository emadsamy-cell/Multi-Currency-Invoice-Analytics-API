# Customer schemas
from app.schemas.customer import (
    CustomerBase,
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
)

# Invoice schemas
from app.schemas.invoice import (
    InvoiceBase,
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
)

# Analytics schemas
from app.schemas.analytics import (
    AnalyticsRequest,
    TotalRevenueResponse,
    AverageInvoiceResponse,
)

__all__ = [
    # Customer schemas
    "CustomerBase",
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerResponse",
    # Invoice schemas
    "InvoiceBase",
    "InvoiceCreate",
    "InvoiceUpdate",
    "InvoiceResponse",
    # Analytics schemas
    "AnalyticsRequest",
    "TotalRevenueResponse",
    "AverageInvoiceResponse",
]

