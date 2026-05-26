import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from app.core.config import settings
from app.scheduler.job import ScannerJob

async def main():
    logger.info("Initializing APScheduler...")
    scheduler = AsyncIOScheduler()
    scanner_job = ScannerJob()
    
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
    
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
