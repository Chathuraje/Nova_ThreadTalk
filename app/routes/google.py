from fastapi import APIRouter, HTTPException
from utils.logger import setup_logger, get_logger
from app.libraries import google
from fastapi import Request
from fastapi import File, UploadFile, Request
from utils.response import GoogleUploadJsonFileResponse, GoogleAuthResponse, GoogleAuthCallbackResponse

setup_logger()
logger = get_logger()

router = APIRouter(
    tags=['Google'],
    prefix='/google'
)


@router.post('/upload-json-file', response_model=GoogleUploadJsonFileResponse)
async def upload_json(file: UploadFile = File(...)):
    logger.info('upload json endpoint accessed.')
    return await google.upload_json(file)

@router.get('/setup_google', response_model=GoogleAuthResponse)
async def setup_google(request: Request):
    logger.info('google setup endpoint accessed.')
    return await google.setup_google(request)

@router.get('/auth_callback', include_in_schema=False, response_model=GoogleAuthCallbackResponse)
async def google_auth_callback(request: Request, code: str):
    logger.info("google_auth_callback endpoint accessed.")
    return await google.google_callback(request, code)

@router.post('/upload_pickle_file', response_model=GoogleUploadJsonFileResponse)
async def upload_pickle_file(request: Request, file: UploadFile = File(...)):
    logger.info('upload pickle endpoint accessed.')
    return await google.upload_pickle_file(request, file)