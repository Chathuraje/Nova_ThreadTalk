from fastapi import APIRouter
from app.libraries import video
from utils.logger import setup_logger, get_logger
from enum import Enum

setup_logger()
logger = get_logger()


router = APIRouter(
    tags=["Videos"],
)

class SubredditEnum(str, Enum):
    AskReddit = "AskReddit"

@router.get("/generate_short_video/{subreddit}")
async def generate_short_video(subreddit: SubredditEnum):
    logger.info("generate short video endpoint accessed")
    
    return await video.generate_short_video(subreddit)
    

@router.get("/get_video_data/{video_id}")
async def get_video_data(video_id: str):
    try:
        video_data = await video.get_video_data(video_id)
        return video_data
    except Exception as e:
        logger.error(f"Error getting video data: {e}")

@router.get('/ongoing_videos')
async def get_ongoing_videos():
    try:
        ongoing_videos = await video.get_ongoing_videos()
        if ongoing_videos == "":
            return {"message": "No ongoing videos"}
        return ongoing_videos
    except Exception as e:
        logger.error(f"Error getting ongoing videos: {e}")

@router.get('/get_all_system_saved_videos')
async def get_all_system_saved_videos():
    try:
        all_videos = await video.get_all_system_saved_videos()
        return all_videos
    except Exception as e:
        logger.error(f"Error getting all videos: {e}")

@router.get('/delete_video/{video_id}')
async def delete_video(video_id: str):
    try:
        await video.delete_video(video_id)
        return {"message": "Video deleted successfully!"}
    except Exception as e:
        logger.error(f"Error deleting video: {e}")