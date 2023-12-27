from utils.log import setup_logger, get_logger
from libraries.setup import schedule

setup_logger()
logger = get_logger()


def generate_timestamp(date, num_times):
    logger.info('Start scheduling videos...')
    dateandtime = schedule.generate_timestamp(date, num_times)
    logger.info('Videos scheduled successfully!')
    return dateandtime

def start_scheduled_videos():
    logger.info('Starting scheduled videos...')
    data = schedule.start_scheduled_videos()
    logger.info('Scheduled videos started successfully!')
    
    return data

def stop_scheduled_videos():
    logger.info('Stopping scheduled videos...')
    schedule.stop_scheduled_videos()
    logger.info('Scheduled videos stopped successfully!')
    
    
def view_scheduled_videos():
    logger.info('Viewing scheduled videos...')
    dateandtime = schedule.view_scheduled_videos()
    logger.info('Scheduled videos fetched successfully!')
    return dateandtime