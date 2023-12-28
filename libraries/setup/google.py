from utils.logger import setup_logger, get_logger
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path

setup_logger()
logger = get_logger()

SCOPES=[
    'https://www.googleapis.com/auth/youtube.force-ssl', 
    'https://www.googleapis.com/auth/drive'
]


def upload_json(file):
    if file.content_type != 'application/json':
        logger.error(f'Only JSON files are allowed')
    
    Path(f"secrets/google").mkdir(parents=True, exist_ok=True)
    file_path = f"secrets/google/threadtalk.json"
    with open(file_path, "wb") as f:
        f.write(file.file.read())
        
    return None
    


def google_callback(request, code):
    try:
        JSON_PATH = 'secrets/google/threadtalk.json'

        flow = InstalledAppFlow.from_client_secrets_file(JSON_PATH, scopes=SCOPES)
        flow.redirect_uri = request.url_for("google_auth_callback")
        flow.fetch_token(code=code)
        
        creds = flow.credentials

        PICKLE_FILE = JSON_PATH.replace('.json', '.pickle')
        with open(PICKLE_FILE, 'wb') as token:
            pickle.dump(creds, token)
            
            logger.info(f'Created token file')

        return creds

    except Exception as e:
        logger.error(f'An error occurred in google_callback: {e}')
        
    

def create_refresh_token(request):
    try:
        JSON_PATH = 'secrets/google/threadtalk.json'
        
        flow = InstalledAppFlow.from_client_secrets_file(
            JSON_PATH, scopes=SCOPES)
        
        flow.redirect_uri = request.url_for("google_auth_callback")
        auth_url, _ = flow.authorization_url(prompt='consent')
        logger.info(f'Please go to this URL: {auth_url}')
        return auth_url
                    
    except Exception as e:
        logger.error(f'Error loading credentials from json file: {e}')


def setup_google(request):
    JSON_PATH = 'secrets/google/threadtalk.json'
    
    logger.info(f'Creating refresh token')
    response = create_refresh_token(request)
        
    return response