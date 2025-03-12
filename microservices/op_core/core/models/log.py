from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import declarative_base
import json

Base = declarative_base()

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    method = Column(String, index=True)
    url = Column(String)
    status_code = Column(Integer)
    request_body = Column(Text, nullable=True)
    response_body = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    process_time = Column(Float)
    sql_queries = Column(Text, nullable=True)  # 🔥 Chứa danh sách SQL dưới dạng JSON
