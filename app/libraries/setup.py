from utils.log import setup_logger, get_logger
import pickle
from libraries.setup import initial_setup

setup_logger()
logger = get_logger()


def setup():
    logger.info(f'Starting setup...')
        
    logger.info('Start downloading background videos...')
    initial_setup.download_background_videos()
    logger.info('Background videos downloaded successfully!')
    
    logger.info('Checking video resolution...')
    initial_setup.check_video_resolution()
    logger.info('Video resolution checked successfully!')
    
    logger.info('Setup completed successfully!')
    