import strawberry
from typing import List, Optional
from app.graphql.types import Customer, Invoice, customer_from_db, invoice_from_db
from app.models import Customer as CustomerModel, Invoice as InvoiceModel


@strawberry.type
class Query:
    
    @strawberry.field
    def customer(self, info, id: int) -> Optional[Customer]:
        db = info.context["db"]
        
        customer = db.query(CustomerModel).filter(
            CustomerModel.id == id,
            CustomerModel.deleted_at.is_(None)
        ).first()
        
        if not customer:
            return None
        
        invoices = db.query(InvoiceModel).filter(
            InvoiceModel.customer_id == customer.id,
            InvoiceModel.deleted_at.is_(None)
        ).all()
        
        return customer_from_db(customer, invoices)
    
    @strawberry.field
    def invoices(
        self,
        info,
        customer_id: Optional[int] = None,
        customer_name: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Invoice]:
        db = info.context["db"]
        
        # By customer ID
        if customer_id:
            invoices = db.query(InvoiceModel).filter(
                InvoiceModel.customer_id == customer_id,
                InvoiceModel.deleted_at.is_(None)
            ).offset(skip).limit(limit).all()
            
            return [invoice_from_db(inv) for inv in invoices]
        
        # By customer name
        elif customer_name:
            customer = db.query(CustomerModel).filter(
                CustomerModel.name.ilike(f"%{customer_name}%"),
                CustomerModel.deleted_at.is_(None)
            ).first()
            
            if not customer:
                return []
            
            invoices = db.query(InvoiceModel).filter(
                InvoiceModel.customer_id == customer.id,
                InvoiceModel.deleted_at.is_(None)
            ).offset(skip).limit(limit).all()
            
            return [invoice_from_db(inv) for inv in invoices]
        
        # All invoices with pagination
        else:
            invoices = db.query(InvoiceModel).filter(
                InvoiceModel.deleted_at.is_(None)
            ).offset(skip).limit(limit).all()
            
            return [invoice_from_db(inv) for inv in invoices]
