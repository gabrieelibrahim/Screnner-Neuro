import yfinance as yf
import pandas as pd
import asyncio
from loguru import logger
from typing import List, Dict, Optional

class YFinanceFetcher:
    def __init__(self):
        self.chunk_size = 100 # Batch size to prevent memory leaks or ban
        
    def _fetch_sync(self, tickers: List[str], period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """
        Synchronous fetch using yfinance batch download.
        """
        tickers_str = " ".join(tickers)
        try:
            # group_by='ticker' will return a MultiIndex dataframe
            df = yf.download(tickers_str, period=period, interval=interval, group_by='ticker', threads=True, progress=False)
            return df
        except Exception as e:
            logger.error(f"Error fetching data from YFinance: {e}")
            return pd.DataFrame()

    async def fetch_batch(self, tickers: List[str], period: str = "1y", interval: str = "1d") -> Dict[str, pd.DataFrame]:
        """
        Asynchronously fetch data in chunks and parse it into a dictionary of DataFrames per ticker.
        """
        results: Dict[str, pd.DataFrame] = {}
        
        for i in range(0, len(tickers), self.chunk_size):
            chunk = tickers[i:i + self.chunk_size]
            logger.info(f"Fetching chunk {i // self.chunk_size + 1}: {len(chunk)} tickers...")
            
            df = await asyncio.to_thread(self._fetch_sync, chunk, period, interval)
            
            if df is None or df.empty:
                logger.warning(f"Empty data received for chunk {i // self.chunk_size + 1}")
                continue

            # Process MultiIndex DataFrame if multiple tickers are requested
            if len(chunk) > 1:
                for ticker in chunk:
                    if ticker in df.columns.levels[0]:
                        ticker_df = df[ticker].dropna(how='all')
                        if not ticker_df.empty:
                            results[ticker] = ticker_df
            else:
                # Single ticker fallback
                ticker = chunk[0]
                ticker_df = df.dropna(how='all')
                if not ticker_df.empty:
                    results[ticker] = ticker_df
                    
            # Brief sleep to avoid hitting rate limits excessively
            await asyncio.sleep(0.5)

        logger.info(f"Successfully fetched data for {len(results)} tickers.")
        return results
