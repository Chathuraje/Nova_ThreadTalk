import os
import google.auth
import google.auth.transport.requests
import google.oauth2.credentials
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from utils.log import setup_logger, get_logger
from datetime import datetime

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

def upload_to_youtube(reddit_details):
    creds = authenticate()
    youtube_client = build_youtube_client(creds)
    
    video_id = reddit_details['id']
    youtube_details = reddit_details['youtube_details']
        
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
        
    response = request.execute()
    video_id = response['id']
    
    video_url = f'https://www.youtube.com/watch?v={video_id}'
    logger.info(f'Video URL is: {video_url}')
        
    # youtube_set_active(youtube_client, video_id)
    
    reddit_details['youtube_details']['upload_date'] = datetime.now().timestamp()
    reddit_details['youtube_details']['url'] = video_url
    reddit_details['youtube_details']['status'] = "uploaded"
    
        
    return reddit_details     
        
        
        
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
       
        
       
    




