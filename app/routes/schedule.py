from fastapi import APIRouter, Query
from utils.logger import setup_logger, get_logger
from app.libraries import schedule
from datetime import datetime, timedelta
from utils.response import ViewScheduledVideoResponse, StopScheduledVideoRespose

setup_logger()
logger = get_logger()

router = APIRouter(
    prefix="/schedule",
    tags=['Schedule Videos'],
)

@router.get("/start_scheduled_videos", response_model=ViewScheduledVideoResponse)
async def start_scheduled_videos():
    logger.info("start_scheduled_videos endpoint accessed.")
    return await schedule.start_scheduled_videos()
   
        
@router.get("/stop_scheduled_videos", response_model=StopScheduledVideoRespose)
async def stop_scheduled_videos():
    logger.info("stop_scheduled_videos endpoint accessed.")
    return await schedule.stop_scheduled_videos()

        
@router.get("/view_scheduled_videos", response_model=ViewScheduledVideoResponse)
async def view_scheduled_videos():
    logger.info("view_scheduled_videos endpoint accessed.")
    return await schedule.view_scheduled_videos()
