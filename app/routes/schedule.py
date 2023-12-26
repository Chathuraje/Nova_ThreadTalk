from fastapi import APIRouter, Query
from utils.log import setup_logger, get_logger
from app.libraries import setup
from datetime import datetime, timedelta

setup_logger()
logger = get_logger()

router = APIRouter(
    prefix="/schedule",
    tags=['Schedule Videos'],
)



@router.get("/schedule_videos")
def schedule_videos(
    date: str = Query(datetime.now().strftime('%Y-%m-%d'), title="Date", description="The date for which to schedule videos, defaults to today."), 
    num_times: int = Query(4, title="Number of Times", description="Number of random times to generate")
):
    try:
        dateandtime = setup.schedule_videos(date, num_times)
        return {"message": "Video scheduling complete.", "data": dateandtime}
    except Exception as e:
        logger.error(f"Error during initial setup: {e}")
        
@router.get("/stop_scheduled_videos")
def stop_scheduled_videos():
    try:
        setup.stop_scheduled_videos()
        return {"message": "Scheduled videos stopped."}
    except Exception as e:
        logger.error(f"Error stopping scheduled videos: {e}")
        
@router.get("/view_scheduled_videos")
def view_scheduled_videos():
    try:
        dateandtime = setup.view_scheduled_videos()
        return {"message": "Scheduled videos fetched.", "data": dateandtime}
    except Exception as e:
        logger.error(f"Error viewing scheduled videos: {e}")