from pydantic import BaseModel, Field, condecimal, conint, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

class AccountBase(BaseModel):
    account_id: str = Field(..., example="ACC-2026-000001")
    account_name: str
    account_type: str
    industry: Optional[str] = None
    country: str
    region: Optional[str] = None
    currency: str = Field(..., min_length=3, max_length=3, example="USD")
    credit_limit: condecimal(gt=0) = 0
    payment_terms_days: conint(gt=0) = 30
    account_status: str = "ACTIVE"

class AccountCreate(AccountBase):
    pass

class AccountRead(AccountBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class QuoteBase(BaseModel):
    quote_id: str = Field(..., example="QTE-2026-000001")
    account_id: int
    quote_date: datetime
    expiry_date: datetime
    currency: str = Field(..., min_length=3, max_length=3)
    subtotal: condecimal(gt=0) = 0
    discount_amount: condecimal(ge=0) = 0
    tax_amount: condecimal(ge=0) = 0
    total_amount: condecimal(gt=0) = 0
    status: str = "DRAFT"

    @validator("expiry_date")
    def expiry_must_be_after_quote(cls, v, values):
        if "quote_date" in values and v <= values["quote_date"]:
            raise ValueError("expiry_date must be after quote_date")
        return v

class QuoteCreate(QuoteBase):
    pass

class QuoteRead(QuoteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
