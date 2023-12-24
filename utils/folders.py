from pathlib import Path
from utils.log import setup_logger, get_logger


setup_logger()
logger = get_logger()


def create_folders(reddit_id):
    logger.info(f"Creating folders for {reddit_id}")
    
    try:
        Path(f"storage/{reddit_id}/image").mkdir(parents=True, exist_ok=True)
        Path(f"storage/{reddit_id}/voice").mkdir(parents=True, exist_ok=True)
        Path(f"storage/{reddit_id}/data").mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Error creating folders for {reddit_id}: {e}")
        exit()