from fastapi import APIRouter
from utils.log import setup_logger, get_logger
from app.libraries import root

setup_logger()
logger = get_logger()


router = APIRouter(
    tags=["Root"],
)

@router.get("/")
def read_root():
    logger.info("Root endpoint accessed.")
    return {"message": "Hello, this is your FastAPI application!"}

@router.get("/read_log")
def read_log():
    try:
        return root.read_log()
    except Exception as e:
        logger.error(f"Error reading log: {e}")

