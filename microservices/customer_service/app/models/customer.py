from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Index, func
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from op_core.core import Base
import uuid

class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False)
    
    # OAuth IDs
    user_id = Column(Integer, nullable=True)
    google_id = Column(String(255), nullable=True)
    facebook_id = Column(String(255), nullable=True)
    yahoo_id = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    otp_verifications = relationship("OTPVerification", back_populates="customer", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_customer_email', 'email'),
        Index('idx_customer_phone', 'phone'),
        Index('idx_customer_user_id', 'user_id'),
        {'extend_existing': True}
    ) 