import strawberry
from typing import Optional, List
from datetime import datetime


@strawberry.type
class Invoice:
    id: int
    customer_id: int
    amount: float
    currency: str
    amount_in_default_currency: Optional[float]
    exchange_rate: Optional[float]
    created_at: datetime


@strawberry.type
class Customer:
    id: int
    name: str
    created_at: datetime
    invoices: List[Invoice]


def customer_from_db(db_customer, invoices):
    return Customer(
        id=db_customer.id,
        name=db_customer.name,
        created_at=db_customer.created_at,
        invoices=[
            Invoice(
                id=inv.id,
                customer_id=inv.customer_id,
                amount=inv.amount,
                currency=inv.currency,
                amount_in_default_currency=inv.amount_in_default_currency,
                exchange_rate=inv.exchange_rate,
                created_at=inv.created_at
            )
            for inv in invoices
        ]
    )


def invoice_from_db(db_invoice):
    return Invoice(
        id=db_invoice.id,
        customer_id=db_invoice.customer_id,
        amount=db_invoice.amount,
        currency=db_invoice.currency,
        amount_in_default_currency=db_invoice.amount_in_default_currency,
        exchange_rate=db_invoice.exchange_rate,
        created_at=db_invoice.created_at
    )

