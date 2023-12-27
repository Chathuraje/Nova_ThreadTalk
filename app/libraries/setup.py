from utils.log import setup_logger, get_logger
from libraries.setup import setup
from libraries.setup import schedule

setup_logger()
logger = get_logger()


def initial_setup():
    logger.info(f'Starting setup...')
        
    logger.info('Start downloading background videos...')
    setup.download_background_videos()
    logger.info('Background videos downloaded successfully!')
    
    logger.info('Checking video resolution...')
    setup.check_video_resolution()
    logger.info('Video resolution checked successfully!')
    
    logger.info('Generating Scheduled Timestamps...')
    schedule.generate_timestamp()
    schedule.start_scheduled_videos()
    logger.info('Scheduled Timestamps generated successfully!')
    
    logger.info('Setup completed successfully!')
    