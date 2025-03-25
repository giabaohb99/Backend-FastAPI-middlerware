from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime
from ..core.constants import CustomerStatus

class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None

class CustomerCreate(CustomerBase):
    user_id: Optional[int] = None
    google_id: Optional[str] = None
    facebook_id: Optional[str] = None
    yahoo_id: Optional[str] = None

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    google_id: Optional[str] = None
    facebook_id: Optional[str] = None
    yahoo_id: Optional[str] = None
    is_verified: Optional[bool] = None

class CustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    is_verified: bool = False
    created_at: datetime
    
    class Config:
        orm_mode = True

# Customer registration schema
class CustomerRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None

class CustomerPagination(BaseModel):
    total: int
    items: List[CustomerResponse]
    page: int
    size: int

# OTP related schemas
class OTPVerificationRequest(BaseModel):
    email: EmailStr
    otp: str

class OTPVerificationResponse(BaseModel):
    success: bool
    message: str
    customer: Optional[CustomerResponse] = None 