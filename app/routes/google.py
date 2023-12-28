from fastapi import APIRouter
from utils.logger import setup_logger, get_logger
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
    try:
        google.upload_json(file)
        return {'message': 'Upload complete.'}
    except Exception as e:
        logger.error(f"Error uploading JSON file to Google: {e}")

@router.get('/setup_google')
def setup_google(request: Request):
    try:
        auth_url = google.setup_google(request)
        return {'message': 'URL generated successfully.', 'auth_url': auth_url}
    except Exception as e:
        logger.error(f"Error setting up Google authentication: {e}")

@router.get('/google_auth_callback', include_in_schema=False)
def google_auth_callback(request: Request, code: str):
    try:
        google.google_callback(request, code)
        return {'message': 'Google login complete.'}
    except Exception as e:
        logger.error(f"Error during Google authentication callback: {e}")