import csv
from loguru import logger
from sqlalchemy import select
from app.database.session import AsyncSessionLocal
from app.models.stock import Stock

async def load_tickers_to_db(csv_path: str = "data/idx_tickers.csv"):
    """
    Load all tickers from CSV into the stocks table.
    Skips duplicates automatically.
    """
    try:
        rows = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ticker = row.get('ticker', '').strip()
                if ticker:
                    rows.append(row)

        async with AsyncSessionLocal() as session:
            inserted = 0
            for row in rows:
                ticker = row['ticker'].strip()
                # Check if ticker already exists
                result = await session.execute(select(Stock).where(Stock.ticker == ticker))
                existing = result.scalar_one_or_none()
                
                if not existing:
                    stock = Stock(
                        ticker=ticker,
                        name=row.get('name', ''),
                        sector=row.get('sector', 'Unknown'),
                        is_active=True
                    )
                    session.add(stock)
                    inserted += 1
            
            await session.commit()
            logger.info(f"Loaded {inserted} new tickers into database (total CSV rows: {len(rows)})")
            
    except Exception as e:
        logger.error(f"Failed to load tickers to DB: {e}")
