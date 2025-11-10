from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List

from app.database import get_db
from app.models import Invoice, Customer
from app.schemas import InvoiceCreate, InvoiceUpdate, InvoiceResponse
from app.services.exchange_rate import get_exchange_rate_to_default
from app.config import settings

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)) -> InvoiceResponse:
    """Create a new invoice with automatic exchange rate calculation."""
    # Check if customer exists
    customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id {invoice.customer_id} not found"
        )
    
    if customer.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer with id {invoice.customer_id} is deleted"
        )
    
    # Get exchange rate and calculate amount in default currency
    exchange_rate = await get_exchange_rate_to_default(invoice.currency)
    amount_in_default_currency = invoice.amount * exchange_rate
    
    # Create invoice
    db_invoice = Invoice(
        customer_id=invoice.customer_id,
        amount=invoice.amount,
        currency=invoice.currency.upper(),
        default_currency=settings.default_currency.upper(),
        exchange_rate=exchange_rate,
        amount_in_default_currency=amount_in_default_currency
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    
    return db_invoice


@router.get("/", response_model=List[InvoiceResponse])
def list_invoices(
    skip: int = 0,
    limit: int = 100,
    customer_id: int = None,
    db: Session = Depends(get_db)
):
    """List all invoices with optional filtering by customer."""
    query = db.query(Invoice).filter(Invoice.deleted_at.is_(None))
    
    if customer_id:
        query = query.filter(Invoice.customer_id == customer_id)
    
    invoices = query.offset(skip).limit(limit).all()
    return invoices


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific invoice by ID."""
    db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    if not db_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with id {invoice_id} not found"
        )
    
    if db_invoice.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invoice with id {invoice_id} is deleted"
        )
    
    return db_invoice


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    invoice_update: InvoiceUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing invoice and recalculate exchange rate if needed."""
    db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    if not db_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with id {invoice_id} not found"
        )
    
    if db_invoice.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invoice with id {invoice_id} is deleted"
        )
    
    exchange_rate = await get_exchange_rate_to_default(db_invoice.currency)
    db_invoice.amount = invoice_update.amount if invoice_update.amount is not None else db_invoice.amount
    db_invoice.currency = invoice_update.currency.upper() if invoice_update.currency is not None else db_invoice.currency
    db_invoice.amount_in_default_currency = db_invoice.amount * exchange_rate
    db_invoice.exchange_rate = exchange_rate

    db.commit()
    db.refresh(db_invoice)
    
    return db_invoice


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    """Soft delete an invoice by ID."""
    db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    if not db_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with id {invoice_id} not found"
        )
    
    if db_invoice.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invoice with id {invoice_id} already deleted"
        )

    db_invoice.deleted_at = func.now()
    db.commit()
    
    return None

