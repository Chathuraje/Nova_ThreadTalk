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
    tiktok.upload_json(file)
    
    return {'message': 'Upload complete.'}

@router.get('/setup_tiktok')
def setup_tiktok(request: Request):
    auth_url = tiktok.setup_tiktok(request)
    
    return {'message': 'Please click this url', 'auth_url': auth_url}

@router.get('/tiktok_auth_callback', include_in_schema=False)
def tiktok_auth_callback(request: Request, code: str, scopes: str, state: str):
    tiktok.tiktok_auth_callback(request, code, scopes, state)
    
    return {"code": code, "scopes": scopes, "state": state}
    