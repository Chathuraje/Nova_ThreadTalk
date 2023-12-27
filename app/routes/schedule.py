from fastapi import APIRouter, Query
from utils.log import setup_logger, get_logger
from app.libraries import schedule
from datetime import datetime, timedelta

setup_logger()
logger = get_logger()

router = APIRouter(
    prefix="/schedule",
    tags=['Schedule Videos'],
)

@router.get("/start_scheduled_videos")
def start_scheduled_videos():
    return schedule.start_scheduled_videos()
   
        
@router.get("/stop_scheduled_videos")
def stop_scheduled_videos():
    schedule.stop_scheduled_videos()

        
@router.get("/view_scheduled_videos")
def view_scheduled_videos():
    try:
        dateandtime = schedule.view_scheduled_videos()
        return {"message": "Scheduled videos fetched.", "data": dateandtime}
    except Exception as e:
        logger.error(f"Error viewing scheduled videos: {e}")