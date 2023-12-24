from fastapi import APIRouter
from utils.log import setup_logger, get_logger
from app.libraries import setup


setup_logger()
logger = get_logger()

router = APIRouter(
    tags=['Setup'],
)

@router.get("/initial_setup")
def initial_setup():
    try:
        setup.initial_setup()
        return {"message": "Initial setup complete."}
    except Exception as e:
        logger.error(f"Error during initial setup: {e}")