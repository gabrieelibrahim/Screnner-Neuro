import csv
import pandas as pd
from loguru import logger
from app.fetchers.yfinance_fetcher import YFinanceFetcher
from app.indicators.technical import TechnicalIndicators
from app.scanners.breakout import BreakoutScanner
from app.ranking.engine import RankingEngine
from app.alerts.manager import AlertManager
from app.database.session import AsyncSessionLocal
from app.models.signal import Signal
from app.models.alert import Alert
from sqlalchemy.ext.asyncio import AsyncSession

class ScannerJob:
    def __init__(self):
        self.fetcher = YFinanceFetcher()
        self.alert_manager = AlertManager()
        self.csv_path = "data/idx_tickers.csv"

    def _load_tickers(self) -> list:
        try:
            df = pd.read_csv(self.csv_path)
            return df['ticker'].dropna().tolist()
        except Exception as e:
            logger.error(f"Failed to load tickers: {e}")
            return []

    async def run(self):
        logger.info("Starting ScannerNeuro Routine...")
        tickers = self._load_tickers()
        if not tickers:
            logger.warning("No tickers found. Aborting scan.")
            return

        # 1. Fetch Market Data
        logger.info(f"Fetching data for {len(tickers)} tickers...")
        raw_data_map = await self.fetcher.fetch_batch(tickers)

        # 2. Compute Indicators & Scan
        breakout_candidates = []
        
        for ticker, df in raw_data_map.items():
            if len(df) < 50: # Ensure minimum history
                continue
                
            df_ta = TechnicalIndicators.calculate_all(df)
            if df_ta.empty:
                continue
                
            latest_row = df_ta.iloc[-1]
            prev_row = df_ta.iloc[-2] if len(df_ta) > 1 else None
            
            # Ensure index name or 'Open'/'Close' columns exist
            latest_row['Open'] = latest_row.get('Open', 0)
            
            is_breakout, reason, metadata = BreakoutScanner.is_breakout(latest_row, prev_row)
            
            if is_breakout:
                # Need original open price for alert % calculation
                metadata['open'] = latest_row['Open'] 
                breakout_candidates.append({
                    "ticker": ticker,
                    "row": latest_row,
                    "metadata": metadata
                })

        logger.info(f"Found {len(breakout_candidates)} raw breakout candidates.")

        # 3. Rank Candidates
        if breakout_candidates:
            ranked_candidates = RankingEngine.rank_candidates(breakout_candidates)
            
            # 4. Save to Database and Process Alerts for Top Candidates
            top_candidates = ranked_candidates[:5]
            
            async with AsyncSessionLocal() as session:
                for cand in top_candidates:
                    ticker = cand['ticker']
                    score = cand['score']
                    meta = cand['metadata']
                    
                    # Simpan ke tabel Signals
                    new_signal = Signal(
                        ticker=ticker,
                        signal_type="BREAKOUT",
                        score=score,
                        price=meta['close'],
                        rvol=meta['rvol'],
                        rsi=meta['rsi'],
                        details=meta
                    )
                    session.add(new_signal)
                    await session.commit()
                    await session.refresh(new_signal)
                    
                    logger.info(f"Processing Alert for Top Candidate: {ticker} (Score: {score})")
                    # Kirim ke Telegram (Cooldown dicek di dalam alert_manager)
                    await self.alert_manager.process_alert(ticker, score, meta, session)
                    
                    # Simpan ke tabel Alerts (opsional track success/fail alert telegram di DB)
                    new_alert = Alert(
                        signal_id=new_signal.id,
                        ticker=ticker,
                        message="Sent via Telegram",
                        status="SENT"
                    )
                    session.add(new_alert)
                    await session.commit()

        logger.info("Scanner Routine Completed.")
