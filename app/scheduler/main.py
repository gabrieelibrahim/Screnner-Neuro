import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from app.core.config import settings
from app.scheduler.job import ScannerJob
from app.utils.load_tickers import load_tickers_to_db
from app.telegram.poller import build_bot_app

async def main():
    logger.info("Initializing APScheduler...")
    scheduler = AsyncIOScheduler()
    scanner_job = ScannerJob()
    
    # Load tickers to db first
    await load_tickers_to_db()
    
    # Run once immediately on startup
    asyncio.create_task(scanner_job.run())
    
    # Schedule recurrent task
    scheduler.add_job(
        scanner_job.run, 
        'interval', 
        minutes=settings.SCAN_INTERVAL_MINUTES,
        id='scanner_neuro_main_job',
        name='Scan IDX stocks for breakouts'
    )
    
    scheduler.start()
    
    bot_app = build_bot_app()
    if bot_app:
        logger.info("Starting Telegram Poller (2-Way Interactive)...")
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling()
    
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down...")
    finally:
        if bot_app:
            await bot_app.updater.stop()
            await bot_app.stop()
            await bot_app.shutdown()
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
