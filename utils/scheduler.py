from utils.log import setup_logger, get_logger
from app.libraries import setup
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

# Setup Logger
setup_logger()
logger = get_logger()

def daily_tasks():
    try:
        logger.info("Running daily scheduler")
        setup.initial_setup()
        logger.info("Daily scheduler finished")
    except Exception as e:
        logger.error(f"Error in daily tasks: {e}")

def add_daily_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.start()

    scheduler.add_job(daily_tasks, 'cron', hour=0, minute=0, timezone=timezone('Asia/Colombo'))
