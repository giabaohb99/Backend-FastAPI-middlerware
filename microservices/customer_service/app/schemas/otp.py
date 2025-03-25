from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, Union, Dict, Any, List
from datetime import datetime
from ..models.otp import OTPType, OTPPurpose

class OTPBase(BaseModel):
    identifier: str  # Email hoặc số điện thoại
    otp_type: str  # EMAIL hoặc PHONE
    otp_purpose: str  # Mục đích sử dụng OTP

    @validator('otp_type')
    def validate_otp_type(cls, v):
        if v not in [t.value for t in OTPType]:
            raise ValueError(f"otp_type must be one of {[t.value for t in OTPType]}")
        return v

    @validator('otp_purpose')
    def validate_otp_purpose(cls, v):
        if v not in [p.value for p in OTPPurpose]:
            raise ValueError(f"otp_purpose must be one of {[p.value for p in OTPPurpose]}")
        return v

class OTPCreate(OTPBase):
    customer_id: Optional[int] = None
    device_info: Optional[str] = None

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

class OTPResendRequest(BaseModel):
    email: EmailStr

class OTPResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    resend_count: Optional[int] = None
    max_resends: Optional[int] = None

class OTPRequest(BaseModel):
    """
    Schema cho yêu cầu OTP mới
    """
    email: EmailStr

class OTPVerify(BaseModel):
    """
    Schema cho xác thực OTP
    """
    email: EmailStr
    otp: str

class OTPInDB(OTPBase):
    id: int
    code: str
    created_at: datetime
    expires_at: datetime
    is_used: bool
    is_sent: bool
    send_count: int
    verify_count: int
    customer_id: Optional[int] = None

    class Config:
        orm_mode = True 