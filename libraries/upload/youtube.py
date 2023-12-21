import os
import google.auth
import google.auth.transport.requests
import google.oauth2.credentials
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from utils.log import setup_logger, get_logger
from utils.data import read_json, check_ongoing, update_json
from utils.time import get_time_after_15_minutes, get_time_after_15_minutes_in_timestamp
from config.config import STAGE
import os

setup_logger()
logger = get_logger()

def auth():
    TOKEN_PATH = 'secrets/google/threadtalk.pickle'
    logger.info(f'Trying to Load credentials from pickle file')
    
    creds = None

    try:
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, 'rb') as token:
                creds = pickle.load(token)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info('Refreshing credentials')
                    creds.refresh(google.auth.transport.requests.Request()) 
                else:
                    logger.error(f'Error loading credentials from pickle file. Needs to be refreshed.')
                    return None
                        
            return creds
        else:
            logger.error(f'Token file not found')
            return None
    except Exception as e:
            logger.error(f'Error loading credentials from pickle file: {e}')


def authenticate():
    return auth()


def build_youtube_client(creds):
    return build('youtube', 'v3', credentials=creds)


def __check_if_video_uploaded(reddit):
    upload_info = reddit["upload_info"]
    if upload_info == []:
        return False
    else:
        youtube_exists = False

        for tag in upload_info:
            if tag['platform'] == 'youtube':
                youtube_exists = True

        return youtube_exists

def upload_to_youtube():
    reddit_id = check_ongoing()
    reddit_details = read_json(reddit_id)
    
    if __check_if_video_uploaded(reddit_details):
        logger.info(f"Post {reddit_id} already has video uploaded. Skipping...")
        return None
    
    creds = authenticate()
    youtube_client = build_youtube_client(creds)
    
    upload_video(reddit_details, youtube_client)
    
    

def upload_video(reddit_details, youtube_client):
    video_id = reddit_details['id']
    meta_tags = reddit_details['meta_tags']
    
    for tag in meta_tags:
        if tag['platform'] == 'youtube':
            youtube_details = tag
            
        
    title = youtube_details['title']
    description = youtube_details['description']
    tags = youtube_details['tags']
    
    request_body = {
        'snippet': {
        'categoryId': 22,
        'title': title,
        'description': description,
        'tags': tags
    },
    'status': {
        'privacyStatus': 'private',
        'selfDeclaredMadeForKids': False,
        'publishAt': get_time_after_15_minutes()
    },
    'notifySubscribers': True
    }
        
    mediaFile = MediaFileUpload(f'storage/{video_id}/{video_id}.mp4')
        
    request = youtube_client.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=mediaFile
    )
        
    if STAGE == 'PRODUCTION':
        response = request.execute()
    elif STAGE == 'DEVELOPMENT':
        response = {'kind': 'youtube#video', 'etag': 'COTIZQV7jGTZMIGUFKdIro5ORfY', 'id': '000000001', 'snippet': {'publishedAt': '2023-12-18T07:50:13Z', 'channelId': 'UCfC0a4Vvw-EoleljN_H5x5w', 'title': 'This is for development only.', 'description': 'This is for development only.', 'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/y3tsZ3oNkUk/default.jpg', 'width': 120, 'height': 90}, 'medium': {'url': 'https://i.ytimg.com/vi/y3tsZ3oNkUk/mqdefault.jpg', 'width': 320, 'height': 180}, 'high': {'url': 'https://i.ytimg.com/vi/y3tsZ3oNkUk/hqdefault.jpg', 'width': 480, 'height': 360}}, 'channelTitle': 'discuss_duo', 'tags': ['This is for development only.'], 'categoryId': '22', 'liveBroadcastContent': 'none', 'localized': {'title': 'This is for development only.', 'description': 'This is for development only.'}}, 'status': {'uploadStatus': 'uploaded', 'privacyStatus': 'public', 'license': 'youtube', 'embeddable': True, 'publicStatsViewable': True, 'selfDeclaredMadeForKids': False}}
    
    video_id = response['id']
    
    video_url = f'https://www.youtube.com/watch?v={video_id}'
    logger.info(f'Video URL is: {video_url}')
    
    reddit_details['upload_info'].append({
        'platform': 'youtube',
        'id': video_id,
        'url': video_url,
        'status': 'uploaded',
        'upload_date': get_time_after_15_minutes_in_timestamp()
    })
    
    update_json(reddit_details)
        
       
    




