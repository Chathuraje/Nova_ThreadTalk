from utils.log import setup_logger, get_logger
import os
import pickle
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import random
import hashlib
import json

setup_logger()
logger = get_logger()

SCOPES=[
    'video.upload'
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
    REDIRECT_URI = request.url_for("callback")
    
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
    
def create_refresh_token(request, client_key)  :
    authorization_url, csrf_state, code_verifier = get_authorization_url(request, client_key)
    logger.info(f'Please visit the following URL to authorize your application:\n{authorization_url}')
    
    authorization_data = [csrf_state, code_verifier]
    TIKTOK_PATH = 'secrets/tiktok/threadtalk.pickle'
    with open(TIKTOK_PATH, 'wb') as f:
        pickle.dump(authorization_data, f)
        
    return authorization_url
    
    
def setup_tiktok(request):
    JSON_PATH = 'secrets/tiktok/threadtalk.json'
    
    with open(JSON_PATH, 'r') as json_file:
        config = json.load(json_file)
    
    client_key = config.get("installed", {}).get("client_key", None)
    
    if client_key:
        logger.info(f'Creating refresh token')
        response = create_refresh_token(request, client_key)
        
        return response
    else:
        logger.error(f'Please upload your TikTok json')