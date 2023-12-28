from utils.log import setup_logger, get_logger
import os
import pickle
from pathlib import Path
import random
import hashlib
import json
import requests

setup_logger()
logger = get_logger()

SCOPES=[
    'video.publish'
]


def upload_json(file):
    if file.content_type != 'application/json':
        logger.error(f'Only JSON files are allowed')
    
    Path(f"secrets/tiktok").mkdir(parents=True, exist_ok=True)
    file_path = f"secrets/tiktok/threadtalk.json"
    with open(file_path, "wb") as f:
        f.write(file.file.read())
        
    return None
    
    
def generate_random_string(length):
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~', k=length))

def get_authorization_url(request, CLIENT_KEY):
    REDIRECT_URI = request.url_for("tiktok_auth_callback")
    
    csrf_state = generate_random_string(6)
    code_verifier = generate_random_string(128)
    code_challenge = hashlib.sha256(code_verifier.encode()).hexdigest()

    authorization_url = 'https://www.tiktok.com/v2/auth/authorize/'
    authorization_url += f'?client_key={CLIENT_KEY}'
    authorization_url += f'&scope={",".join(SCOPES)}'
    authorization_url += '&response_type=code'
    authorization_url += f'&redirect_uri={REDIRECT_URI}'
    authorization_url += f'&state={csrf_state}'
    authorization_url += f'&code_challenge={code_challenge}'
    authorization_url += '&code_challenge_method=S256'

    return authorization_url, csrf_state, code_verifier    
    
def get_authorization_code(request, client_key)  :
    authorization_url, csrf_state, code_verifier = get_authorization_url(request, client_key)
    logger.info(f'Please visit the following URL to authorize your application: {authorization_url}')
    
    authorization_data = [csrf_state, code_verifier]
    TIKTOK_PATH = 'secrets/tiktok/threadtalk.pickle'
    with open(TIKTOK_PATH, 'wb') as f:
        pickle.dump(authorization_data, f)
        
    return authorization_url
    
def get_config():
    TIKTOK_PATH = 'secrets/tiktok/threadtalk.json'
    with open(TIKTOK_PATH, 'r') as f:
        config = json.load(f)
        
    return config['auth'] 
    
    
def setup_tiktok(request):
    config = get_config()
    
    client_key = config['client_key']
    if client_key is not None:
        logger.info(f'Creating refresh token')
        response = get_authorization_code(request, client_key)
        
        return response
    else:
        logger.error(f'Please upload your TikTok json')
        
    
def save_token_data(token_data):
    TIKTOK_PATH = 'secrets/tiktok/threadtalk.pickle'
    with open(TIKTOK_PATH, 'wb') as f:
        pickle.dump(token_data, f)

def get_access_token(request, code, code_verifier):
    config = get_config()
    REDIRECT_URI = request.url_for("tiktok_auth_callback")
    
    token_url = 'https://open.tiktokapis.com/v2/oauth/token/'
    params = {
        'client_key': config['client_key'],
        'client_secret': config['client_secret'],
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code',
        'code_verifier': code_verifier,
    }

    response = requests.post(token_url, data=params)
    return response.json()   
    
    
    
def tiktok_auth_callback(request, code, scopes, state):
    TIKTOK_PATH = 'secrets/tiktok/threadtalk.pickle'
    if not os.path.exists(TIKTOK_PATH):
        logger.error('No authorization data found. Exiting...')
        
    with open(TIKTOK_PATH, 'rb') as f:
        authorization_data = pickle.load(f)
    
    try: 
        csrf_state = authorization_data[0]
        code_verifier = authorization_data[1]
            
        if state != csrf_state:
            logger.error('CSRF state mismatch. Exiting...')
            return

        token_data = get_access_token(request, code, code_verifier)

        save_token_data(token_data)
        logger.info('Token data saved')
    except Exception as e:
        logger.error(f'Authorization url was expired. Please try again')