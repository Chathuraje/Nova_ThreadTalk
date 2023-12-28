from fastapi import APIRouter
from utils.logger import setup_logger, get_logger
from app.libraries import setup
from fastapi import File, UploadFile, Request


setup_logger()
logger = get_logger()

router = APIRouter(
    tags=['Setup'],
)

@router.post('/upload_json_secrets')
def upload_json_secrets(file: UploadFile = File(...)):
    try:
        setup.upload_json_secrets(file)
        return {'message': 'Upload complete.'}
    except Exception as e:
        logger.error(f"Error uploading JSON file to Google: {e}")

@router.get("/initial_setup")
def initial_setup():
    try:
        setup.initial_setup()
        return {"message": "Initial setup complete."}
    except Exception as e:
        logger.error(f"Error during initial setup: {e}")