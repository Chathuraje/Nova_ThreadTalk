from utils.log import setup_logger, get_logger
from libraries.setup import google

setup_logger()
logger = get_logger()

def upload_json(file):
    logger.info('Uploading json')
    google.upload_json(file)
    logger.info('Upload complete.')
    
    return None

def google_callback(request, code):
    google.google_callback(request, code)
    
    logger.info('Google login complete.')
    return None


def setup_google(request):
    logger.info('Setting up Google')
    return google.setup_google(request)