from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, description="Customer name (required)")


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str = Field(..., min_length=1, description="Customer name (required)")


class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

