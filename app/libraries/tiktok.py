from utils.log import setup_logger, get_logger
from libraries.setup import tiktok

setup_logger()
logger = get_logger()


def upload_json(file):
    logger.info('Uploading json')
    tiktok.upload_json(file)
    logger.info('Upload complete.')
    
    return None

def setup_tiktok(request):
    logger.info('Setting up TikTok')
    return tiktok.setup_tiktok(request)


def tiktok_callback(request, code, scopes, state):
    tiktok.tiktok_callback(request, code, scopes, state)
    
    logger.info('TikTok login complete.')
    return None