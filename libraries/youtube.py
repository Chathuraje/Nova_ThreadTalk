import os
import google.auth
import google.auth.transport.requests
import google.oauth2.credentials
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from utils.log import setup_logger, get_logger

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

def upload_to_youtube(complete_data):
    creds = authenticate()
    youtube_client = build_youtube_client(creds)
    data = []
    for video_file in complete_data:
        video_id = video_file['id']
        youtube_meta_data = video_file['youtube_meta_data']
        
        title = youtube_meta_data['title']
        description = youtube_meta_data['description']
        tags = youtube_meta_data['tags']
        
        request_body = {
            'snippet': {
                'categoryId': 22,
                'title': title,
                'description': description,
                'tags': tags
            },
            'status': {
                'privacyStatus': 'unlisted',
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
        
        video_data = youtube_set_active(youtube_client, video_id, video_file)
        data.append(video_data)
        
    return data     
        
        
def youtube_set_active(youtube, video_id: str, video_file):
    
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
    
    video_file['youtube_meta_data']['url'] = video_url
    
    return video_file
       
        
       
    




