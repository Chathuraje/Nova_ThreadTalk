from fastapi import APIRouter, HTTPException
from utils.logger import setup_logger, get_logger
from app.libraries import root
from utils.response import StandardResponse, ReadLogResponse

setup_logger()
logger = get_logger()


router = APIRouter(
    tags=["Root"],
)

@router.get("/", response_model=StandardResponse)
async def read_root():
    logger.info("Root endpoint accessed.")
    return await root.root()

@router.get("/read-log", response_model=ReadLogResponse)
async def read_log(limit: int = None):
    logger.info("Log endpoint accessed.")
    return await root.read_log(limit)

