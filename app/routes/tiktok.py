from fastapi import APIRouter
from utils.logger import setup_logger, get_logger
from fastapi import Request
from fastapi import File, UploadFile, Request
from app.libraries import tiktok
from utils.response import TiktokUploadJsonFileResponse, TiktokAuthResponse, TiktokAuthCallbackResponse


setup_logger()
logger = get_logger()

router = APIRouter(
    tags=['TikTok'],
    prefix='/tiktok'
)

@router.post('/tiktok_upload-json-file', response_model=TiktokUploadJsonFileResponse)
async def upload_json(file: UploadFile = File(...)):
    logger.info('upload json endpoint accessed.')
    return await tiktok.upload_json(file)

@router.get('/tiktok_setup_tiktok', response_model=TiktokAuthResponse)
async def setup_tiktok(request: Request):
    logger.info('tiktok setup endpoint accessed.')
    return await tiktok.setup_tiktok(request)

@router.get('/tiktok_auth_callback', include_in_schema=False, response_model=TiktokAuthCallbackResponse)
async def tiktok_auth_callback(request: Request, code: str, scopes: str, state: str):
    logger.info("tiktok_auth_callback endpoint accessed.")
    return await tiktok.tiktok_auth_callback(request, code, scopes, state)

@router.post('/upload_pickle_file', response_model=TiktokUploadJsonFileResponse)
async def upload_pickle_file(request: Request, file: UploadFile = File(...)):
    logger.info('upload pickle endpoint accessed.')
    return await tiktok.upload_pickle_file(request, file)