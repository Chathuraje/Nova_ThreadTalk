from utils.logger import setup_logger, get_logger
import os
import pickle
from pathlib import Path
import random
import hashlib
import json
import requests
from fastapi import HTTPException
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
from utils.response import TiktokUploadContent
from utils.tiktokToken import TikTokTokenData

setup_logger()
logger = get_logger()

SCOPES=[
    'video.publish'
]
class TiktokClientConfig(BaseModel):
    apps_id: str
    client_key: str
    client_secret: str
    csrf_state: Optional[str] = None
    code_verifier: Optional[str] = None

class TiktokConfig(BaseModel):
    auth: Optional[TiktokClientConfig]
    
async def upload_json(file) -> TiktokUploadContent:
    if file.content_type != 'application/json':
        logger.error('Invalid file type, only JSON files are allowed.')
        raise HTTPException(status_code=400, detail='Invalid file type, only JSON files are allowed.')
    
    try:
        Path("secrets/tiktok").mkdir(parents=True, exist_ok=True)
        file_path = "secrets/tiktok/threadtalk.json"
        content = await file.read()
        json_data = json.loads(content.decode('utf-8'))
        
        validated_data = None
        if 'auth' in json_data:
            validated_data = TiktokConfig(**json_data)
        else:
            raise AttributeError("No valid 'auth' configuration found in JSON file.")

        with open(file_path, "w") as f:
            json.dump(validated_data.dict(), f, indent=4)
        
        return TiktokUploadContent(upload_status="Success")

    except ValidationError as e:
        logger.error(f"JSON values are missing or wrong: {e.json()}")
        raise HTTPException(status_code=422, detail=f"JSON values are missing or wrong")
    except AttributeError as e:
            logger.error(f'No valid configuration found in JSON file: {e}')
            raise HTTPException(status_code=500, detail=f"No valid configuration found in JSON file: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except IOError as e:
        logger.error(f"File IO Error: {e}")
        raise HTTPException(status_code=500, detail="File saving failed")
    except Exception as e:
        logger.error(f"Unknown error: {e}")
        raise HTTPException(status_code=500, detail=f"Unknown error: {e}")
    
async def setup_tiktok(request):
    
    JSON_PATH = "secrets/tiktok/threadtalk.json"
    if not os.path.exists(JSON_PATH):
        logger.error("TikTok configuration file not found.")
        raise HTTPException(status_code=500, detail="TikTok configuration file not found.")
    
    try:
        flow = TikTokTokenData()
        flow.setup_from_client_secrets_file(JSON_PATH, SCOPES)
        flow.redirect_uri = request.url_for("tiktok_auth_callback")
        
        auth_url = flow.get_authorization_url()
        return auth_url

    except Exception as e:
        logger.error(f"Error in setup_tiktok: {e}")
        raise HTTPException(status_code=500, detail=f"Error in setup_tiktok: {e}")

    
def save_token_data(token_data):
    tiktok_token_data = TikTokTokenData(**token_data)
    
    TIKTOK_PATH = 'secrets/tiktok/threadtalk.pickle'
    with open(TIKTOK_PATH, 'wb') as f:
        pickle.dump(tiktok_token_data, f)

    
async def tiktok_auth_callback(request, code, scopes, state):
    JSON_PATH = "secrets/tiktok/threadtalk.json"
    if not os.path.exists(JSON_PATH):
        logger.error("TikTok configuration file not found.")
        raise HTTPException(status_code=500, detail="TikTok configuration file not found.")
    
    try:
        flow = TikTokTokenData()
        flow.setup_from_client_secrets_file(JSON_PATH, SCOPES)
        flow.redirect_uri = request.url_for("tiktok_auth_callback")
        
        token_data = flow.get_refresh_token(request, code, scopes, state)
        save_token_data(token_data)

    except FileExistsError as e:
        logger.error(f"Error in setup_tiktok: {e}")
        raise HTTPException(status_code=500, detail=f"Error in setup_tiktok: {e}")
    except ValueError as e:
        logger.error(f"Error in setup_tiktok: {e}")
        raise HTTPException(status_code=500, detail=f"Error in setup_tiktok: {e}")
    
    
    
async def upload_pickle_file(request, file) -> TiktokUploadContent:
    if file.content_type != 'application/octet-stream':
        logger.error('Invalid file type, only pickle files are allowed.')
        raise HTTPException(status_code=400, detail='Invalid file type, only pickle files are allowed.')
    
    try:
        content = await file.read()
        pickle_file_path = 'secrets/tiktok/threadtalk.pickle'
        with open(pickle_file_path, "wb") as f:
            f.write(content)
        
        return TiktokUploadContent(upload_status="Success")
    except IOError as e:
        logger.error(f"File IO Error: {e}")
        raise HTTPException(status_code=500, detail="File saving failed")
    except Exception as e:
        logger.error(f"Unknown error: {e}")
        raise HTTPException(status_code=500, detail=f"Unknown error: {e}")