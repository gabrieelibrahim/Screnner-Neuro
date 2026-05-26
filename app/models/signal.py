from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from app.models.base import Base

class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), ForeignKey("stocks.ticker", ondelete="CASCADE"), index=True)
    
    signal_type = Column(String(50), index=True) # e.g. "BREAKOUT", "MOMENTUM"
    score = Column(Float) # Ranking score
    
    price = Column(Float)
    rvol = Column(Float)
    rsi = Column(Float)
    
    # New Confirmation Fields
    breakout_confirmed = Column(Boolean, default=False)
    breakout_strength = Column(Float, default=0.0)
    breakout_volume_score = Column(Float, default=0.0)
    
    details = Column(JSON) # Simpan metadata tambahan (alasan lolos filter)
    
    timestamp = Column(DateTime(timezone=True), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
