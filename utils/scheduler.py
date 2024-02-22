from utils.logger import setup_logger, get_logger
from app.libraries import setup
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# Setup Logger
setup_logger()
logger = get_logger()

async def daily_tasks():
    try:
        logger.info("Running daily scheduler")
        await setup.initial_setup()
        logger.info("Daily scheduler finished")
    except Exception as e:
        logger.error(f"Error in daily tasks: {e}")

async def add_daily_scheduler():
    Appscheduler = AsyncIOScheduler()
    Appscheduler.start()
    await daily_tasks()
    
    Appscheduler.add_job(daily_tasks, 'cron', hour=0, minute=0, timezone=timezone('Asia/Colombo'))
