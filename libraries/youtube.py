import os
import google.auth
import google.auth.transport.requests
import google.oauth2.credentials
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from utils.log import setup_logger, get_logger
from utils.data import read_json, check_ongoing, update_json
from utils.time import get_current_sri_lankan_time
from config.config import STAGE


setup_logger()
logger = get_logger()

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
# define the path to the token.pickle file

def authenticate():
    TOKEN_PATH = f'config/google/google.pickle'
    
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            # create the OAuth2 flow for user authorization
            JSON_PATH = f'config/google/digitix_607367205827.json'
            flow = InstalledAppFlow.from_client_secrets_file(
                JSON_PATH, scopes=SCOPES)
            creds = flow.run_local_server(port=0)
            # save the credentials to the token.pickle file for later use
            
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            # save the credentials for next time
            with open(TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
    # return the authenticated credentials
    return creds


# build the YouTube API client
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
        'privacyStatus': 'public',
        'selfDeclaredMadeForKids': False
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
        
    # youtube_set_active(youtube_client, video_id)
    
    reddit_details['upload_info'].append({
        'platform': 'youtube',
        'id': video_id,
        'url': video_url,
        'status': 'uploaded',
        'upload_date': get_current_sri_lankan_time()
    })
        
    update_json(reddit_details)
        
        
def youtube_set_active(youtube, video_id: str):
    
    request = youtube.videos().update(
    part='status',
    body={
        'id': video_id,
        'status': {
            'privacyStatus': 'public'
        }})
    
    request.execute()
    video_url = f'https://www.youtube.com/watch?v={video_id}'
    logger.info(f'Video URL is: {video_url}')
       
        
       
    




