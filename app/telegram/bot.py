import httpx
from loguru import logger
from app.core.config import settings

class TelegramNotifier:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    async def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram Bot Token or Chat ID not configured.")
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.base_url, json=payload, timeout=10.0)
                if response.status_code == 200:
                    logger.info(f"Telegram alert sent successfully.")
                    return True
                else:
                    logger.error(f"Failed to send Telegram alert: {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Telegram API Exception: {e}")
            return False
