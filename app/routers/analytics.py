from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models import Invoice
from app.schemas import AnalyticsRequest, TotalRevenueResponse, AverageInvoiceResponse
from app.services.exchange_rate import ExchangeRateService
from app.config import settings

router = APIRouter(prefix="/analytics", tags=["Analytics"])


async def convert_invoice_to_currency(
    invoice: Invoice,
    target_currency: str,
    exchange_service: ExchangeRateService
) -> float:
    """
    Convert an invoice amount to the target currency.
    
    Args:
        invoice: The invoice to convert
        target_currency: The currency to convert to
        exchange_service: The exchange rate service instance
    
    Returns:
        float: The converted amount in the target currency
    """
    # If invoice currency matches target, return original amount
    if invoice.currency.upper() == target_currency.upper():
        return invoice.amount
    
    # Otherwise, fetch current exchange rate and convert
    exchange_rate = await exchange_service.get_exchange_rate(
        from_currency=invoice.currency,
        to_currency=target_currency
    )
    return invoice.amount * exchange_rate


def build_invoice_query(
    db: Session,
    customer_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """
    Build a query for invoices with optional filters.
    
    Args:
        db: Database session
        customer_id: Optional customer ID filter
        start_date: Optional start date filter
        end_date: Optional end date filter
    
    Returns:
        SQLAlchemy query object
    """
    query = db.query(Invoice).filter(Invoice.deleted_at.is_(None))
    
    if customer_id:
        query = query.filter(Invoice.customer_id == customer_id)
    
    if start_date:
        query = query.filter(Invoice.created_at >= start_date)
    
    if end_date:
        query = query.filter(Invoice.created_at <= end_date)
    
    return query


@router.post("/total-revenue", response_model=TotalRevenueResponse)
async def get_total_revenue(
    analytics_request: AnalyticsRequest,
    db: Session = Depends(get_db)
) -> TotalRevenueResponse:
    """
    Calculate total revenue from all invoices, converted to the specified currency.
    
    This endpoint:
    - Fetches all relevant invoices based on optional filters
    - Converts each invoice to the target currency using current exchange rates
    - Sums up the converted amounts to provide total revenue
    
    Query Parameters:
    - target_currency: Currency to convert revenue to (defaults to system default)
    - customer_id: Filter by specific customer
    - start_date: Filter invoices from this date onwards
    - end_date: Filter invoices up to this date
    """
    # Determine target currency
    target_currency = analytics_request.target_currency or settings.default_currency
    target_currency = target_currency.upper()
    
    # Build query with filters
    query = build_invoice_query(
        db=db,
        customer_id=analytics_request.customer_id,
        start_date=analytics_request.start_date,
        end_date=analytics_request.end_date
    )
    
    # Fetch invoices
    invoices = query.all()
    
    if not invoices:
        return TotalRevenueResponse(
            total_revenue=0.0,
            currency=target_currency,
            invoice_count=0,
            start_date=analytics_request.start_date,
            end_date=analytics_request.end_date,
            customer_id=analytics_request.customer_id
        )
    
    # Convert and sum amounts
    exchange_service = ExchangeRateService()
    total_revenue = 0.0
    
    for invoice in invoices:
        converted_amount = await convert_invoice_to_currency(
            invoice=invoice,
            target_currency=target_currency,
            exchange_service=exchange_service
        )
        total_revenue += converted_amount
    
    return TotalRevenueResponse(
        total_revenue=round(total_revenue, 2),
        currency=target_currency,
        invoice_count=len(invoices),
        start_date=analytics_request.start_date,
        end_date=analytics_request.end_date,
        customer_id=analytics_request.customer_id
    )


@router.post("/average-invoice", response_model=AverageInvoiceResponse)
async def get_average_invoice_size(
    analytics_request: AnalyticsRequest,
    db: Session = Depends(get_db)
) -> AverageInvoiceResponse:
    """
    Calculate the average invoice size, converted to the specified currency.
    
    This endpoint:
    - Fetches all relevant invoices based on optional filters
    - Converts each invoice to the target currency using current exchange rates
    - Calculates the average invoice amount
    
    Query Parameters:
    - target_currency: Currency to convert average to (defaults to system default)
    - customer_id: Filter by specific customer
    - start_date: Filter invoices from this date onwards
    - end_date: Filter invoices up to this date
    """
    # Determine target currency
    target_currency = analytics_request.target_currency or settings.default_currency
    target_currency = target_currency.upper()
    
    # Build query with filters
    query = build_invoice_query(
        db=db,
        customer_id=analytics_request.customer_id,
        start_date=analytics_request.start_date,
        end_date=analytics_request.end_date
    )
    
    # Fetch invoices
    invoices = query.all()
    
    if not invoices:
        return AverageInvoiceResponse(
            average_invoice_size=0.0,
            currency=target_currency,
            invoice_count=0,
            start_date=analytics_request.start_date,
            end_date=analytics_request.end_date,
            customer_id=analytics_request.customer_id
        )
    
    # Convert and sum amounts
    exchange_service = ExchangeRateService()
    total_revenue = 0.0
    
    for invoice in invoices:
        converted_amount = await convert_invoice_to_currency(
            invoice=invoice,
            target_currency=target_currency,
            exchange_service=exchange_service
        )
        total_revenue += converted_amount
    
    # Calculate average
    average_invoice_size = total_revenue / len(invoices)
    
    return AverageInvoiceResponse(
        average_invoice_size=round(average_invoice_size, 2),
        currency=target_currency,
        invoice_count=len(invoices),
        start_date=analytics_request.start_date,
        end_date=analytics_request.end_date,
        customer_id=analytics_request.customer_id
    )

