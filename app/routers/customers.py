from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List

from app.database import get_db
from app.models import Customer, Invoice
from app.schemas import CustomerCreate, CustomerUpdate, CustomerResponse

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)) -> CustomerResponse:
    """Create a new customer."""
    db_customer = Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    
    return db_customer


@router.get("/", response_model=List[CustomerResponse])
def list_customers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all customers."""
    customers = db.query(Customer).filter(Customer.deleted_at.is_(None)).offset(skip).limit(limit).all()
    return customers


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing customer."""
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not db_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id {customer_id} not found"
        )
    
    if db_customer.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer with id {customer_id} already deleted"
        )
    
    # Update fields
    update_data = customer_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_customer, field, value)
    
    db.commit()
    db.refresh(db_customer)
    
    return db_customer

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """Delete a customer by ID and cascade soft delete all related invoices."""
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not db_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id {customer_id} not found"
        )
    
    if db_customer.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer with id {customer_id} already deleted"
        )

    # Soft delete the customer
    deletion_time = func.now()
    db_customer.deleted_at = deletion_time
    
    # Cascade soft delete all related invoices
    db.query(Invoice).filter(
        Invoice.customer_id == customer_id,
        Invoice.deleted_at.is_(None)
    ).update(
        {Invoice.deleted_at: deletion_time},
        synchronize_session=False
    )
    
    db.commit()
    
    return None