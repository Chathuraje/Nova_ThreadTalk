from utils.logger import setup_logger, get_logger
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path
from fastapi import HTTPException
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
import json
from utils.response import GoogleUploadContent, GoogleAuthContent, GoogleAuthCallbackContent
from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError

setup_logger()
logger = get_logger()

SCOPES=[
    'https://www.googleapis.com/auth/youtube.force-ssl', 
    'https://www.googleapis.com/auth/drive'
]

class GoogleClientConfig(BaseModel):
    client_id: str
    project_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_secret: str
    redirect_uris: Optional[List[str]] = None
    javascript_origins: Optional[List[str]] = None

class GoogleConfigInstalled(BaseModel):
    installed: Optional[GoogleClientConfig]
    
class GoogleConfigWeb(BaseModel):
    web: Optional[GoogleClientConfig]

async def upload_json(file) -> GoogleUploadContent:
    if file.content_type != 'application/json':
        logger.error('Invalid file type, only JSON files are allowed.')
        raise HTTPException(status_code=400, detail='Invalid file type, only JSON files are allowed.')

    try:
        Path("secrets/google").mkdir(parents=True, exist_ok=True)
        content = await file.read()
        json_data = json.loads(content.decode('utf-8'))
        
        validated_data = None
        if 'web' in json_data:
            validated_data = GoogleConfigWeb(**json_data)
        elif 'installed' in json_data:
            validated_data = GoogleConfigInstalled(**json_data)
        else:
            raise AttributeError("No valid 'web' or 'installed' configuration found in JSON file.")

        file_path = "secrets/google/threadtalk.json"
        with open(file_path, "w") as f:
            json.dump(validated_data.dict(), f, indent=4)
        
        return GoogleUploadContent(upload_status="Success")

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


async def setup_google(request) -> GoogleAuthContent:
    logger.info(f'Creating refresh token')
    JSON_PATH = 'secrets/google/threadtalk.json'
    
    try:
        with open(JSON_PATH, 'r') as f:
            json_data = json.load(f)

        validated_data = None
        if 'web' in json_data:
            validated_data = GoogleConfigWeb(**json_data)
        elif 'installed' in json_data:
            validated_data = GoogleConfigInstalled(**json_data)
        else:
            raise AttributeError("No valid 'web' or 'installed' configuration found in JSON file.")
        
        flow = InstalledAppFlow.from_client_secrets_file(JSON_PATH, scopes=SCOPES)
        flow.redirect_uri = f"https://{request.headers['host']}/google/auth_callback"
        auth_url, _ = flow.authorization_url(prompt='consent')
        logger.info(f'Please go to this URL: {auth_url}')
        return auth_url
    
    except FileNotFoundError:
        logger.error('JSON configuration file not found')
        raise HTTPException(status_code=404, detail="JSON configuration file not found")
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
    


async def google_callback(request, code):
    JSON_PATH = 'secrets/google/threadtalk.json'
    try:
        with open(JSON_PATH, 'r') as f:
            json_data = json.load(f)

        validated_data = None
        if 'web' in json_data:
            validated_data = GoogleConfigWeb(**json_data)
        elif 'installed' in json_data:
            validated_data = GoogleConfigInstalled(**json_data)
        else:
            raise AttributeError("No valid 'web' or 'installed' configuration found in JSON file.")

            
        flow = InstalledAppFlow.from_client_secrets_file(JSON_PATH, scopes=SCOPES)
        flow.redirect_uri = f"https://{request.headers['host']}/google/auth_callback"
        flow.fetch_token(code=code)

        creds = flow.credentials
        PICKLE_FILE = JSON_PATH.replace('.json', '.pickle')

        with open(PICKLE_FILE, 'wb') as token:
            pickle.dump(creds, token)
            logger.info('Created token file')
            
    
    except FileNotFoundError:
        logger.error('JSON configuration file not found')
        raise HTTPException(status_code=404, detail="JSON configuration file not found")
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
        
        
async def upload_pickle_file(request, file) -> GoogleUploadContent:
    if file.content_type != 'application/octet-stream':
        logger.error('Invalid file type, only pickle files are allowed.')
        raise HTTPException(status_code=400, detail='Invalid file type, only pickle files are allowed.')
    
    try:
        content = await file.read()
        pickle_file_path = 'secrets/google/threadtalk.pickle'
        with open(pickle_file_path, "wb") as f:
            f.write(content)
        
        return GoogleUploadContent(upload_status="Success")
    except IOError as e:
        logger.error(f"File IO Error: {e}")
        raise HTTPException(status_code=500, detail="File saving failed")
    except Exception as e:
        logger.error(f"Unknown error: {e}")
        raise HTTPException(status_code=500, detail=f"Unknown error: {e}")