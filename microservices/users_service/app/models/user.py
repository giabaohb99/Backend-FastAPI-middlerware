from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from op_core.core import Base
import time

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    status = Column(Integer, default=1)  # Default status is 1 (active)
    created_at = Column(Integer, default=int(time.time()))  # Lấy số nguyên từ time.time()
    updated_at = Column(Integer, default=int(time.time())) 