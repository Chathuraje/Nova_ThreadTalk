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



@router.get("/generate_timestamp")
def generate_timestamp(
    date: str = Query(datetime.now().strftime('%Y-%m-%d'), title="Date", description="The date for which to schedule videos, defaults to today."), 
    num_times: int = Query(4, title="Number of Times", description="Number of random times to generate")
):
    try:
        dateandtime = schedule.generate_timestamp(date, num_times)
        return {"message": "Video scheduling complete.", "data": dateandtime}
    except Exception as e:
        logger.error(f"Error during initial setup: {e}")
        



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