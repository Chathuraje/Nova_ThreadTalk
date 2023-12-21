import os
from utils.log import setup_logger, get_logger
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from tqdm import tqdm
import time
from pathlib import Path
import cv2
from libraries.upload.youtube import authenticate

setup_logger()
logger = get_logger()


def build_google_drive_client(creds):
    logger.info("Building Google Drive Client...")
    
    return build('drive', 'v3', credentials=creds)
    
def find_folders(GOOGLE_SERVICE):
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
    
    
    return folder_founds['Nova_ThreadTalk']['id'], folder_founds['Background_Videos']['id']

    
def download_background_videos():
    creds = authenticate()
    GOOGLE_SERVICE = build_google_drive_client(creds)
    Path(f"data/background_videos").mkdir(parents=True, exist_ok=True)
    
    try:
        _, background_folder_id = find_folders(GOOGLE_SERVICE)
        
        results = GOOGLE_SERVICE.files().list(q=f"'{background_folder_id}' in parents", fields="files(id, name)").execute()
        files = results.get('files', [])
        
        if not files:
            logger.error('No background videos found in the specified folder. Please upload files to the folder and try again. (Video Width: 2160 pixels: 2160x4096)')
            exit(1)
        else:
            for file in files:
                file_id = file['id']
                file_name = file['name']
                
                if os.path.exists(os.path.join('data/background_videos', file_name)):
                    logger.info(f'{file_name} already exists. Skipping...')
                    continue
                
                logger.info(f'Downloading {file_name}...')
                download_file(GOOGLE_SERVICE, file_id, file_name, 'data/background_videos')
    except Exception as e:
        logger.error(f'Error creating folders. Please create it manually: {e}')
            

def download_file(drive_service, file_id, file_name, destination_folder):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(os.path.join(destination_folder, file_name), 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    start_time = time.time()
    with tqdm(total=100, desc=f"Downloading {file_name}", unit="%", unit_scale=True) as pbar:
        while not done:
            status, done = downloader.next_chunk()
            progress = int(status.progress() * 100)
            pbar.update(progress - pbar.n)
            
            # Calculate and display download speed
            elapsed_time = time.time() - start_time
            download_speed = status.total_size / 1024 / elapsed_time  # in KB/s
            pbar.set_postfix(speed=f"{download_speed:.2f} KB/s")

    pbar.close()


def check_video_resolution():
    background_video_path = f"data/background_videos/"
    all_files = os.listdir(background_video_path)
    video_files = [file for file in all_files if file.endswith(('.mp4', '.avi', '.mkv', '.mov'))]
    VIDEO_WIDTH = 2160

    for file in video_files:
        video_path = os.path.join(background_video_path, file)
        
        logger.info(f"Checking video resolution for {file}...")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Error: Could not open video file. {file}")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        cap.release()
        logger.info(f"Video resolution: {width}x{height}")
        
        if width != VIDEO_WIDTH:
            logger.warn(f"Error: Video width should be {VIDEO_WIDTH} pixels. {file} is {width} pixels wide.")
            os.remove(video_path)
            logger.info(f"Video deleted: {file}")