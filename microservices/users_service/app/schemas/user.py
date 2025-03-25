from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from ..core.constants import UserStatus

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    status: Optional[int] = UserStatus.ACTIVE.value

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserLogout(BaseModel):
    token: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    status: Optional[int] = None

class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class User(UserInDBBase):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: int  # user_id
    exp: datetime 