from fastapi import APIRouter
from utils.log import setup_logger, get_logger
from fastapi import Request
from fastapi import File, UploadFile, Request
from app.libraries import tiktok


setup_logger()
logger = get_logger()

router = APIRouter(
    tags=['TikTok'],
)

@router.post('/upload_json_tiktok')
def upload_json(file: UploadFile = File(...)):
    try:
        tiktok.upload_json(file)
        return {'message': 'Upload complete.'}
    except Exception as e:
        logger.error(f"Error uploading JSON file to TikTok: {e}")

@router.get('/setup_tiktok')
def setup_tiktok(request: Request):
    try:
        auth_url = tiktok.setup_tiktok(request)
        return {'message': 'URL generated successfully.', 'auth_url': auth_url}
    except Exception as e:
        logger.error(f"Error setting up TikTok authentication: {e}")

@router.get('/tiktok_auth_callback', include_in_schema=False)
def tiktok_auth_callback(request: Request, code: str, scopes: str, state: str):
    try:
        tiktok.tiktok_auth_callback(request, code, scopes, state)
        return {"code": code, "scopes": scopes, "state": state}
    except Exception as e:
        logger.error(f"Error during TikTok authentication callback: {e}")
