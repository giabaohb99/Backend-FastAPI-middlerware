from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from datetime import datetime
from .. import Base

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    method = Column(String(10), nullable=False)  # HTTP method (GET, POST, etc.)
    url = Column(String(255), nullable=False)  # Request URL
    status_code = Column(Integer)  # Response status code
    request_body = Column(Text, nullable=True)  # Request body if any
    response_body = Column(Text, nullable=True)  # Response body if any
    ip_address = Column(String(50))  # Client IP address
    user_agent = Column(String(255))  # User agent string
    process_time = Column(Float)  # Request processing time in seconds
    created_at = Column(DateTime, default=datetime.utcnow)  # When the log was created 