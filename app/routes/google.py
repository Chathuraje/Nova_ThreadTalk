from fastapi import APIRouter
from utils.log import setup_logger, get_logger
from app.libraries import google
from fastapi import Request
from fastapi import File, UploadFile, Request

setup_logger()
logger = get_logger()

router = APIRouter(
    tags=['Google'],
)


@router.post('/upload_json_google')
def upload_json(file: UploadFile = File(...)):
    google.upload_json(file)
    
    return {'message': 'Upload complete.'}

@router.get('/setup_google')
def setup_google(request: Request):
    auth_url = google.setup_google(request)
    
    return {'message': 'Please click this url', 'auth_url': auth_url}

@router.get('/google_auth_callback', include_in_schema=False)
def google_auth_callback(request: Request, code: str):
    google.google_callback(request, code)
    
    return {'message': 'Google login complete.'}
    