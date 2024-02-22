from utils.logger import setup_logger, get_logger
from libraries.setup import tiktok
from utils.response import TiktokUploadJsonFileResponse, TiktokAuthResponse, TiktokAuthCallbackResponse

setup_logger()
logger = get_logger()


async def upload_json(file) -> TiktokUploadJsonFileResponse:
    data = await tiktok.upload_json(file)

    return TiktokUploadJsonFileResponse(code=200, data=data)


async def setup_tiktok(request) -> TiktokAuthResponse:
    auth_url = await tiktok.setup_tiktok(request)
    
    return TiktokAuthResponse(code=200, data={'auth_url': auth_url})


async def tiktok_auth_callback(request, code, scopes, state) -> TiktokAuthCallbackResponse:
    await tiktok.tiktok_auth_callback(request, code, scopes, state)
    
    return TiktokAuthCallbackResponse(code=200, data={'auth_status': 'Success'})


async def upload_pickle_file(request, file) -> TiktokUploadJsonFileResponse:
    data = await tiktok.upload_pickle_file(request, file)
    
    return TiktokUploadJsonFileResponse(code=200, data=data)