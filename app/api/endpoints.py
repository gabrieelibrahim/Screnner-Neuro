from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Dict, Any

from app.database.session import get_db
from app.models.stock import Stock
from app.models.signal import Signal

router = APIRouter()

@router.get("/stocks")
async def get_stocks(limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Retrieve list of active stocks"""
    query = select(Stock).where(Stock.is_active == True).limit(limit)
    result = await db.execute(query)
    stocks = result.scalars().all()
    return {"status": "success", "data": stocks}

@router.get("/signals")
async def get_signals(limit: int = 50, db: AsyncSession = Depends(get_db)):
    """Retrieve latest trading signals (breakout, momentum, etc)"""
    query = select(Signal).order_by(desc(Signal.timestamp)).limit(limit)
    result = await db.execute(query)
    signals = result.scalars().all()
    return {"status": "success", "data": signals}

@router.get("/breakouts")
async def get_breakouts(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Retrieve only the latest breakout setups"""
    query = select(Signal).where(Signal.signal_type == "BREAKOUT").order_by(desc(Signal.timestamp)).limit(limit)
    result = await db.execute(query)
    breakouts = result.scalars().all()
    return {"status": "success", "data": breakouts}

@router.get("/momentum")
async def get_momentum(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Retrieve momentum stocks based on score"""
    # Assuming top score signals are momentum candidates
    query = select(Signal).order_by(desc(Signal.score)).limit(limit)
    result = await db.execute(query)
    momentum = result.scalars().all()
    return {"status": "success", "data": momentum}

@router.get("/top-rvol")
async def get_top_rvol(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Retrieve stocks with highest relative volume"""
    query = select(Signal).order_by(desc(Signal.rvol)).limit(limit)
    result = await db.execute(query)
    top_rvol = result.scalars().all()
    return {"status": "success", "data": top_rvol}

@router.get("/market-summary")
async def get_market_summary(db: AsyncSession = Depends(get_db)):
    """Retrieve daily market analytics summary"""
    # In a full app, this would aggregate data from the MarketData table
    return {
        "status": "success",
        "summary": "Breakout setups are heavily concentrated in the Mining and Banking sectors today with elevated RVOL activity."
    }
