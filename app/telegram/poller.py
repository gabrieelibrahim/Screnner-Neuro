from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from loguru import logger
from app.core.config import settings
from app.database.session import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    username = update.effective_user.username
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.chat_id == chat_id))
        user = result.scalar_one_or_none()
        
        if not user:
            new_user = User(chat_id=chat_id, username=username)
            session.add(new_user)
            await session.commit()
            await update.message.reply_text("✅ Selamat datang! Anda sekarang berlangganan sinyal Breakout Neuro Screener.")
            logger.info(f"New user registered: {username} ({chat_id})")
        else:
            if not user.is_active:
                user.is_active = True
                await session.commit()
                await update.message.reply_text("✅ Langganan diaktifkan kembali.")
            else:
                await update.message.reply_text("✅ Anda sudah berlangganan.")

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong! Neuro Screener sedang berjalan dan siap mencari cuan.")

def build_bot_app():
    # We must not run this if no token is provided
    if not settings.TELEGRAM_BOT_TOKEN:
        return None
        
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("ping", ping_command))
    return app
