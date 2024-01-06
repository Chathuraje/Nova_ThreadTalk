from fastapi import APIRouter
from utils.logger import setup_logger, get_logger
from app.libraries import setup
from fastapi import File, UploadFile, Request
from utils.response import UploadJsonFileResponse, InitialSetupResponse


setup_logger()
logger = get_logger()

router = APIRouter(
    tags=['Setup'],
    prefix='/setup'
)

@router.post('/upload-json-file', response_model=UploadJsonFileResponse)
async def upload_json(file: UploadFile = File(...)):
    logger.info('upload json endpoint accessed.')
    return await setup.upload_json(file)


@router.get("/initial_setup", response_model=InitialSetupResponse)
async def initial_setup():
    logger.info('initial setup endpoint accessed.')
    return await setup.initial_setup()