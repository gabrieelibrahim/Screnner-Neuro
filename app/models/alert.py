from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(Integer, ForeignKey("signals.id", ondelete="CASCADE"), unique=True)
    ticker = Column(String(20), index=True)
    
    message = Column(String)
    telegram_message_id = Column(String(100), nullable=True)
    status = Column(String(50)) # e.g., "SENT", "FAILED"
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
