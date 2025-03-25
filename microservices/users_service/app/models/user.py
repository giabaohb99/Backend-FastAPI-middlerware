from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from op_core.core import Base
import time

class User(Base):
    __tablename__ = "users"

    u_id = Column(Integer, primary_key=True, index=True)
    u_email = Column(String(256), unique=True, index=True, nullable=False)
    u_password = Column(String(255), nullable=False)
    u_fullname = Column(String(255))
    u_activatedcode = Column(String(255), nullable=True)
    u_status = Column(Integer, default=0)  # Default status is 0 (inactive)
    u_datecreated = Column(Integer, default=int(time.time()))
    u_datemodified = Column(Integer, default=int(time.time()))
    u_datelastlogin = Column(Integer, default=0)

    # Relationship with UserToken
    tokens = relationship("UserToken", back_populates="user", cascade="all, delete-orphan")

    # Properties to maintain API compatibility
    @property
    def id(self):
        return self.u_id

    @property
    def email(self):
        return self.u_email

    @property
    def username(self):
        return self.u_email  # Using email as username

    @property
    def hashed_password(self):
        return self.u_password
    
    @hashed_password.setter
    def hashed_password(self, value):
        self.u_password = value

    @property
    def full_name(self):
        return self.u_fullname
    
    @full_name.setter
    def full_name(self, value):
        self.u_fullname = value

    @property
    def status(self):
        return self.u_status
    
    @status.setter
    def status(self, value):
        self.u_status = value

    @property
    def created_at(self):
        return datetime.fromtimestamp(self.u_datecreated)

    @property
    def updated_at(self):
        return datetime.fromtimestamp(self.u_datemodified)

    def update_last_login(self):
        """Update last login time to current timestamp"""
        self.u_datelastlogin = int(time.time()) 