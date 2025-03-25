from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from op_core.core import Base
import time

class UserToken(Base):
    __tablename__ = "user_tokens"

    uk_id = Column(Integer, primary_key=True, index=True)
    uk_user_id = Column(Integer, ForeignKey("users.u_id"), nullable=False)
    uk_access_token = Column(String(500), nullable=False, unique=True, index=True)
    uk_device_info = Column(String(500))  # User agent info
    uk_ip_address = Column(String(50))
    uk_created_at = Column(Integer, default=int(time.time()))
    uk_expires_at = Column(Integer)
    uk_is_active = Column(Integer, default=1)  # 1: active, 0: revoked/expired

    # Relationship with User model
    user = relationship("User", back_populates="tokens")

    def is_valid(self) -> bool:
        """Check if token is still valid"""
        current_time = int(time.time())
        return (self.uk_is_active == 1 and 
                self.uk_expires_at > current_time) 