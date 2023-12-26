from utils.log import setup_logger, get_logger
from libraries.schedule import schedule

setup_logger()
logger = get_logger()


def schedule_videos(date, num_times):
    logger.info('Start scheduling videos...')
    dateandtime = schedule.schedule_videos(date, num_times)
    logger.info('Videos scheduled successfully!')
    return dateandtime

def stop_scheduled_videos():
    logger.info('Stopping scheduled videos...')
    schedule.stop_scheduled_videos()
    logger.info('Scheduled videos stopped successfully!')
    
    
def view_scheduled_videos():
    logger.info('Viewing scheduled videos...')
    dateandtime = schedule.view_scheduled_videos()
    logger.info('Scheduled videos fetched successfully!')
    return dateandtime