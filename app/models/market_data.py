from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, BigInteger, Index
from sqlalchemy.sql import func
from app.models.base import Base

class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), ForeignKey("stocks.ticker", ondelete="CASCADE"), index=True)
    
    timestamp = Column(DateTime(timezone=True), index=True)
    
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(BigInteger)
    
    # Tambahan indikator (opsional) disimpen jika perlu untuk keperluan backtest cepat
    ema_20 = Column(Float, nullable=True)
    ema_50 = Column(Float, nullable=True)
    ema_200 = Column(Float, nullable=True)
    rsi_14 = Column(Float, nullable=True)
    rvol = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_market_data_ticker_time', 'ticker', 'timestamp', unique=True),
    )
