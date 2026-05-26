from typing import Dict, Any
import redis.asyncio as redis
from app.core.config import settings
from app.telegram.bot import TelegramNotifier
from loguru import logger

class AlertManager:
    def __init__(self):
        self.notifier = TelegramNotifier()
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        # Cooldown per ticker in seconds (e.g., 2 hours = 7200 seconds)
        self.cooldown_seconds = 7200 

    async def _is_in_cooldown(self, ticker: str) -> bool:
        key = f"alert_cooldown:{ticker}"
        exists = await self.redis_client.exists(key)
        return bool(exists)

    async def _set_cooldown(self, ticker: str):
        key = f"alert_cooldown:{ticker}"
        await self.redis_client.setex(key, self.cooldown_seconds, "1")

    def _format_alert(self, ticker: str, score: float, data: Dict[str, Any]) -> str:
        clean_ticker = ticker.replace('.JK', '')
        change_pct = ((data['close'] - data['open']) / data['open']) * 100 if data.get('open', 0) > 0 else 0
        
        msg = (
            f"🔥 <b>BREAKOUT ALERT</b> 🔥\n\n"
            f"<b>Ticker:</b> #{clean_ticker}\n"
            f"<b>Price:</b> Rp {data['close']:,.0f} ({change_pct:+.1f}%)\n"
            f"<b>RVOL:</b> {data['rvol']:.1f}x\n"
            f"<b>RSI:</b> {data['rsi']:.1f}\n"
            f"<b>Score:</b> {score:.1f}/100\n\n"
            f"<i>ScannerNeuro IDX Engine</i>"
        )
        return msg

    async def process_alert(self, ticker: str, score: float, data: Dict[str, Any], db_session=None):
        """
        Check cooldown, send telegram message, set cooldown, and optionally log to DB.
        """
        if await self._is_in_cooldown(ticker):
            logger.debug(f"Ticker {ticker} is in cooldown. Skipping alert.")
            return

        message = self._format_alert(ticker, score, data)
        success = await self.notifier.send_message(message)
        
        if success:
            await self._set_cooldown(ticker)
            # You can also insert the alert record into PostgreSQL using db_session here
