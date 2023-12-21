from fastapi import APIRouter
from app.libraries import generate_short_video as _generate_short_video
from libraries.setup import initial_setup as _initial_setup
from utils.log import setup_logger, get_logger
from config.config import STAGE
import pickle
import json
import requests

setup_logger()
logger = get_logger()

router = APIRouter(
    tags=['setup'],
)

@router.get("/initial_setup")
def initial_setup():
    _initial_setup()
    
    return {"message": "Initial setup completed!"}

CLIENT_KEY = '' 
CLIENT_SECRET = '' 
REDIRECT_URI = '' 
SCOPE = '' 


def save_token_data(token_data):
    TIKTOK_PATH = 'config/tiktok/digiix.pickle'
    with open(TIKTOK_PATH, 'wb') as f:
        pickle.dump(token_data, f)

def get_access_token(code, code_verifier):
    token_url = 'https://open.tiktokapis.com/v2/oauth/token/'
    params = {
        'client_key': CLIENT_KEY,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code',
        'code_verifier': code_verifier,
    }

    response = requests.post(token_url, data=params)
    return response.json()

@router.get("/callback/")
def oauth_callback(
    code: str,
    scopes: str,
    state: str
):
    TIKTOK_PATH = 'config/tiktok/digiix.pickle'
    with open(TIKTOK_PATH, 'rb') as f:
        authorization_data = pickle.load(f)
        
    csrf_state = authorization_data[0]
    code_verifier = authorization_data[1]
        
    if state != csrf_state:
        print('CSRF state mismatch. Exiting...')
        return

    token_data = get_access_token(code, code_verifier)
    print(f'Token Data: {token_data}')

    save_token_data(token_data)
    print('Token data saved to token_data.json')
        
    return {"code": code, "scopes": scopes, "state": state}