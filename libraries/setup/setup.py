import os
from utils.logger import setup_logger, get_logger
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from tqdm import tqdm
import time
from pathlib import Path
import cv2
from libraries.upload.youtube import authenticate
from fastapi import HTTPException
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
import json
from utils.response import UploadContent
from fastapi import HTTPException
from googleapiclient.errors import HttpError

setup_logger()
logger = get_logger()


def build_google_drive_client(creds):
    try:
        drive = build('drive', 'v3', credentials=creds)
        return drive
    except Exception as e:
        logger.error(f'Error building YouTube client: {e}')
        raise HTTPException(status_code=500, detail="Failed to build YouTube client")
    
def find_folders(GOOGLE_SERVICE):
    try:
        folders = GOOGLE_SERVICE.files().list(q="mimeType='application/vnd.google-apps.folder' and trashed=false").execute().get('files', [])
    
        logger.info("Checking if folder exists...")
        folder_founds = {}
        for folder in folders:
            if folder.get('name') == "Nova_ThreadTalk":
                folder_founds["Nova_ThreadTalk"] = folder
                logger.info("Nova_ThreadTalk folder found!")
                
            if folder.get('name') == "Background_Videos":
                folder_founds["Background_Videos"] = folder
                logger.info("Background_Videos folder found!")
                
            if len(folder_founds) == 2:
                break
        
        
        if folder_founds.get("Nova_ThreadTalk") == None:
            logger.info("Creating Nova_ThreadTalk folder...")
            parent_folder = GOOGLE_SERVICE.files().create(body={"name": "Nova_ThreadTalk", "mimeType": "application/vnd.google-apps.folder"}, fields="id").execute()
            folder_founds["Nova_ThreadTalk"] = parent_folder
        
        if folder_founds.get("Background_Videos") == None:
            logger.info("Creating Background_Videos folder...")
            background_video_folder = GOOGLE_SERVICE.files().create(body={"name": "Background_Videos", "mimeType": "application/vnd.google-apps.folder", "parents": [folder_founds['Nova_ThreadTalk']['id']]}, fields="id").execute()
            folder_founds["Background_Videos"] = background_video_folder
    
    
    except HttpError as e:
        logger.error(f'Google Drive API error: {e}')
        raise HTTPException(status_code=500, detail='Error interacting with Google Drive API.')

    except Exception as e:
        logger.error(f'Unexpected error while finding folders: {e}')
        raise HTTPException(status_code=500, detail='Error interacting with Google Drive API.')

    return folder_founds['Nova_ThreadTalk']['id'], folder_founds['Background_Videos']['id']

    
async def download_background_videos():
    video_list = []
    try:
        creds = authenticate()
        GOOGLE_SERVICE = build_google_drive_client(creds)
        Path(f"data/background_videos").mkdir(parents=True, exist_ok=True)

        _, background_folder_id = find_folders(GOOGLE_SERVICE)

        results = GOOGLE_SERVICE.files().list(q=f"'{background_folder_id}' in parents", fields="files(id, name)").execute()
        files = results.get('files', [])

        if not files:
            logger.error('No background videos found in the specified folder.')
            raise HTTPException(status_code=404, detail='Background videos not found in the folder.')

        for file in files:
            file_id = file['id']
            file_name = file['name']

            if os.path.exists(os.path.join('data/background_videos', file_name)):
                logger.info(f'{file_name} already exists. Skipping...')
                continue

            logger.info(f'Downloading {file_name}...')
            download_file(GOOGLE_SERVICE, file_id, file_name, 'data/background_videos')
            video_list.append(file_name)
            
        return video_list

    except HttpError as e:
        logger.error(f'Google API error: {e}')
        raise HTTPException(status_code=500, detail='Error interacting with Google Drive API.')
    except FileNotFoundError as e:
        logger.error(f'File not found: {e}')
        raise HTTPException(status_code=404, detail='File not found.')
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        raise HTTPException(status_code=500, detail='An unexpected error occurred.')

            

def download_file(drive_service, file_id, file_name, destination_folder):
    try:
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.FileIO(os.path.join(destination_folder, file_name), 'wb')
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        start_time = time.time()
        with tqdm(total=100, desc=f"Downloading...", unit="%", unit_scale=True) as pbar:
            while not done:
                status, done = downloader.next_chunk()
                progress = int(status.progress() * 100)
                pbar.update(progress - pbar.n)
                
                # Calculate and display download speed
                elapsed_time = time.time() - start_time
                download_speed = status.total_size / 1024 / elapsed_time  # in KB/s
                pbar.set_postfix(speed=f"{download_speed:.2f} KB/s")

        pbar.close()
        
    except HttpError as e:
        logger.error(f'Google Drive API error: {e}')
        raise HTTPException(status_code=500, detail='Error interacting with Google Drive API.')

    except Exception as e:
        logger.error(f'Unexpected error while finding folders: {e}')
        raise HTTPException(status_code=500, detail='Error interacting with Google Drive API.')

    return True


async def check_video_resolution():
    background_video_path = "data/background_videos/"
    VIDEO_WIDTH = 2160
    file_list = []

    if not os.path.exists(background_video_path):
        logger.error(f"Directory does not exist: {background_video_path}")
        raise HTTPException(status_code=404, detail="Video directory not found")

    try:
        all_files = os.listdir(background_video_path)
    except Exception as e:
        logger.error(f"Error accessing files in the directory: {e}")
        raise HTTPException(status_code=500, detail="Error accessing video directory")

    video_files = [file for file in all_files if file.endswith(('.mp4', '.avi', '.mkv', '.mov'))]

    for file in video_files:
        video_path = os.path.join(background_video_path, file)
        logger.info(f"Checking video resolution for {file}...")

        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Could not open video file: {file}")
                continue

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()

            logger.info(f"Video resolution: {width}x{height}")

            if width != VIDEO_WIDTH:
                logger.warning(f"Video width should be {VIDEO_WIDTH} pixels. {file} is {width} pixels wide.")
                os.remove(video_path)
                logger.info(f"Video deleted: {file}")
            file_list.append(file)

        except Exception as e:
            logger.error(f"Error processing file {file}: {e}")
            continue
        
    return file_list
            
     
class RedditConfig(BaseModel):
    client_id: str
    client_secret: str
    user_agent: str
    username: str
    password: str

class ElevenLabsConfig(BaseModel):
    api_keys: List[str]

class MongoDBConfigDetails(BaseModel):
    url: str
    username: str
    password: str

class MongoDBConfig(BaseModel):
    production: MongoDBConfigDetails
    development: MongoDBConfigDetails

class OpenAIConfig(BaseModel):
    api_key: str

class TelegramConfig(BaseModel):
    bot_token: str
    production_channel_id: str
    development_channel_id: str

class Config(BaseModel):
    stage: str
    reddit: RedditConfig
    elevenlabs: ElevenLabsConfig
    mongodb: MongoDBConfig
    openai: OpenAIConfig
    telegram: TelegramConfig
    
       
async def upload_json(file) -> UploadContent:
    if file.content_type != 'application/json':
        logger.error('Invalid file type, only JSON files are allowed.')
        raise HTTPException(status_code=400, detail='Invalid file type, only JSON files are allowed.')
    
    try:
        Path(f"secrets").mkdir(parents=True, exist_ok=True)
        content = await file.read()
        json_data = json.loads(content.decode('utf-8'))
        
        validated_data = Config(**json_data)

        file_path = "secrets/secrets.json"
        with open(file_path, "w") as f:
            json.dump(validated_data.dict(), f, indent=4)
        
        return UploadContent(upload_status="Success")
    
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