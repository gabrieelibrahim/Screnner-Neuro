from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.models.base import Base

class Stock(Base):
    __tablename__ = "stocks"

    ticker = Column(String(20), primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    sector = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
