import os
import google.auth
import google.auth.transport.requests
import google.oauth2.credentials
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from utils.log import setup_logger, get_logger
from utils.data import read_json, check_ongoing, update_json
from utils.time import get_time_after_15_minutes, get_time_after_15_minutes_in_timestamp, get_current_sri_lankan_time
from config.config import STAGE
import os
import json
import requests
import math
from tqdm import tqdm 
import time

from utils.log import setup_logger, get_logger


setup_logger()
logger = get_logger()
    
    
def auth():
    TOKEN_PATH = 'secrets/tiktok/threadtalk.pickle'
    logger.info(f'Trying to Load credentials from pickle file')
    
    creds = None

    try:
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, 'rb') as token:
                creds = pickle.load(token)
                logger.info(f'Credentials loaded from pickle file')
            # if not creds or not creds.valid:
            #     if creds and creds.expired and creds.refresh_token:
            #         logger.info('Refreshing credentials')
            #         creds.refresh(google.auth.transport.requests.Request()) 
            #     else:
            #         logger.error(f'Error loading credentials from pickle file. Needs to be refreshed.')
            #         return None
                        
            return creds
        else:
            logger.error(f'Token file not found')
            return None
    except Exception as e:
            logger.error(f'Error loading credentials from pickle file: {e}')
            
            
def authenticate():
    return auth()   

def __check_if_video_uploaded(reddit):
    upload_info = reddit["upload_info"]
    if upload_info == []:
        return False
    else:
        youtube_exists = False

        for tag in upload_info:
            if tag['platform'] == 'tiktok':
                youtube_exists = True

        return youtube_exists



def initialize_video_upload(access_token, video_path, tiktok_details):
    
    title = tiktok_details['title']
    description = tiktok_details['description']
    tags_string  = tiktok_details['tags']
    
    tags = tags_string.split(',')
    tags_with_hashtags = ' '.join(['#' + tag for tag in tags])

    merged_text = f"{description} {tags_with_hashtags}"
    
    url = 'https://open.tiktokapis.com/v2/post/publish/inbox/video/init/'

    # Set headers
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json; charset=UTF-8'
    }
    
    video_size = os.path.getsize(video_path)
    min_chunk_size = 5 * 1024 * 1024  # 5 MB
    max_chunk_size = 10 * 1024 * 1024  # 10 MB - MAX: 64 MB
    
    total_chunk_count = math.ceil(video_size / max_chunk_size)
    if video_size < min_chunk_size:
        chunk_size = video_size
    else:
        chunk_size = max(min_chunk_size, min(max_chunk_size, video_size // total_chunk_count))
    
    total_chunk_count = max(min(total_chunk_count, 1000), 1)
    logger.info(f'Video: video_length: {video_size}, total_chunk_count: {total_chunk_count}, chunk_size: {chunk_size}')
    
    
    body = {
        "post_info": {
            "title": title,
            "description": merged_text,
            "privacy_level": "PUBLIC_TO_EVERYONE",
        },
        'source_info': {
            'source': 'FILE_UPLOAD',
            'video_size': video_size,
            'chunk_size': chunk_size,
            'total_chunk_count': total_chunk_count
        },
        
    }

    body_json = json.dumps(body)

    response = requests.post(url, headers=headers, data=body_json)
    
    if response.status_code == 200:
        data = response.json()['data']
        publish_id = data['publish_id']
        upload_url = data['upload_url']
        return publish_id, upload_url, video_size, chunk_size, total_chunk_count
    else:
        logger.error(f"Error: {response.status_code}, {response.text}")
        return None, None

def upload_video_chunk(upload_url, chunk_start, chunk_end, video_path):
    file_size = os.path.getsize(video_path)
    headers = {
        'Content-Type': 'video/mp4',
        'Content-Range': f'bytes {chunk_start}-{chunk_end}/{file_size}',
    }

    with open(video_path, 'rb') as file:
        file.seek(chunk_start)
        chunk_data = file.read(chunk_end - chunk_start + 1)

    response = requests.put(upload_url, headers=headers, data=chunk_data)

    return response.status_code
    
    
def upload_chunk_by_chunk(reddit_details, video_path, chunk_size, total_chunk_count, video_size, upload_url, publish_id, video_id):
    for chunk in tqdm(range(total_chunk_count)):
        chunk_start = chunk * chunk_size
        chunk_end = min(chunk_start + chunk_size - 1, video_size - 1)
                    
        if chunk == total_chunk_count - 1:
            chunk_end = video_size - 1
                
        success = upload_video_chunk(upload_url, chunk_start, chunk_end, video_path)
        if success == 201:
            time.sleep(5)
            logger.info(f'Video uploaded successfully.')
            video_url = f'https://www.tiktok.com/@threadtalk/video/{publish_id}'
            logger.info(f"Video uploaded successfully: {video_url}")
            
            video_id = reddit_details['id']       
            reddit_details['upload_info'].append({
                'platform': 'tiktok',
                'id': video_id,
                'url': video_url,
                'status': 'uploaded',
                'upload_date': get_current_sri_lankan_time()
            })
                        
            update_json(reddit_details)
                        
        elif success == 206:
            continue
        else:
            logger.error(f'Error uploading video: {success}')
            return None 
    
    

def upload_video(reddit_details, creds):
    video_id = reddit_details['id']
    meta_tags = reddit_details['meta_tags']
    
    if not meta_tags:
        logger.error("Video upload failed: Meta tags not found.")
    
    video_path = f'storage/{video_id}/{video_id}.mp4'
    for tag in meta_tags:  
        if tag['platform'] == 'tiktok':
            publish_id, upload_url, video_size, chunk_size, total_chunk_count = initialize_video_upload(creds['access_token'], video_path, tag)
            logger.info(f'Publish ID: {publish_id}, URL: {upload_url}')
            
            if publish_id and upload_url:
                upload_chunk_by_chunk(reddit_details, video_path, chunk_size, total_chunk_count, video_size, upload_url, publish_id)
            else:
                logger.error(f'Error uploading video: {publish_id}, {upload_url}')
                return None


def upload_to_tikTok():
    reddit_id = check_ongoing()
    reddit_details = read_json(reddit_id)
    
    if __check_if_video_uploaded(reddit_details):
        logger.info(f"Post {reddit_id} already has video uploaded. Skipping...")
        return None
    
    creds = authenticate()
    upload_video(reddit_details, creds)
    
    
    
    
    
    
    
    