from utils.log import setup_logger, get_logger
from libraries.setup import setup

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
    
    logger.info('Setup completed successfully!')
    