from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from op_core.core import Base
from op_core.core.config import settings
import enum

class OTPType(enum.Enum):
    """Loại OTP"""
    EMAIL = "EMAIL"
    PHONE = "PHONE"

class OTPPurpose(enum.Enum):
    """Mục đích sử dụng OTP"""
    REGISTRATION = "REGISTRATION"
    PASSWORD_RESET = "PASSWORD_RESET"
    LOGIN = "LOGIN"
    VERIFY_EMAIL = "VERIFY_EMAIL"
    VERIFY_PHONE = "VERIFY_PHONE"

class OTPVerification(Base):
    """Model lưu trữ thông tin OTP"""
    __tablename__ = "otp_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(255), nullable=False, index=True)  # Email hoặc số điện thoại
    otp_type = Column(String(20), nullable=False, default=OTPType.EMAIL.value)
    otp_purpose = Column(String(50), nullable=False, default=OTPPurpose.REGISTRATION.value)
    code = Column(String(10), nullable=True)  # OTP code được tạo ngẫu nhiên
    is_used = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    send_count = Column(Integer, default=0)  # Số lần đã gửi OTP
    verify_count = Column(Integer, default=0)  # Số lần đã thử xác thực
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=True)
    device_info = Column(Text, nullable=True)  # Thông tin thiết bị yêu cầu OTP

    # Relationship với Customer model
    customer = relationship("Customer", back_populates="otp_verifications")
    
    # Table args
    __table_args__ = (
        Index('idx_otp_identifier', 'identifier'),
        Index('idx_otp_customer_id', 'customer_id'),
        {'extend_existing': True}
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Tạo mã OTP ngẫu nhiên nếu không được cung cấp
        if "code" not in kwargs:
            from app.core.email_utils import generate_otp
            self.code = generate_otp(settings.OTP_LENGTH)
        
        # Tính thời gian hết hạn nếu không được cung cấp
        if "expires_at" not in kwargs:
            self.expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

    @property
    def is_expired(self) -> bool:
        """Kiểm tra OTP đã hết hạn chưa"""
        return datetime.utcnow() > self.expires_at

    @property
    def can_resend(self) -> bool:
        """Kiểm tra có thể gửi lại OTP không (tránh spam)"""
        if self.send_count >= settings.OTP_MAX_RESENDS:
            return False  # Đã vượt quá số lần gửi lại tối đa
        
        time_since_last_send = datetime.utcnow() - self.created_at
        return time_since_last_send.total_seconds() >= (settings.OTP_COOLDOWN_MINUTES * 60)

    @property
    def exceeded_attempts(self) -> bool:
        """Kiểm tra đã vượt quá số lần thử cho phép chưa"""
        return self.verify_count >= settings.OTP_MAX_ATTEMPTS 