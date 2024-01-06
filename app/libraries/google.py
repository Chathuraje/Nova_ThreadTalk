from utils.logger import setup_logger, get_logger
from libraries.setup import google
from utils.response import GoogleUploadJsonFileResponse, GoogleAuthResponse, GoogleAuthCallbackResponse

setup_logger()
logger = get_logger()

async def upload_json(file) -> GoogleUploadJsonFileResponse:
    data = await google.upload_json(file)
    
    return GoogleUploadJsonFileResponse(code=200, data=data)

async def setup_google(request) -> GoogleAuthResponse:
    auth_url = await google.setup_google(request)
    
    return GoogleAuthResponse(code=200, data={'auth_url': auth_url})

async def google_callback(request, code) -> GoogleAuthCallbackResponse:
    await google.google_callback(request, code)
    
    return GoogleAuthCallbackResponse(code=200, data={'auth_status': 'Success'})