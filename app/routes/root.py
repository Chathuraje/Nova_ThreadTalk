from fastapi import APIRouter
from utils.logger import setup_logger, get_logger
from app.libraries import root
from utils.response import StandardResponse, LogContent

setup_logger()
logger = get_logger()


router = APIRouter(
    tags=["Root"],
)

@router.get("/", response_model=StandardResponse)
def read_root():
    logger.info("Root endpoint accessed.")
    return root.root()

@router.get("/read-log", response_model=StandardResponse[LogContent])
def read_log(limit: int = None):
    logger.info("Log endpoint accessed.")
    return root.read_log(limit)

