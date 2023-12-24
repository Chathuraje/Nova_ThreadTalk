from fastapi import APIRouter
from app.libraries import video
from utils.log import setup_logger, get_logger
from enum import Enum

setup_logger()
logger = get_logger()


router = APIRouter(
    tags=["Videos"],
)

class SubredditEnum(str, Enum):
    AskReddit = "AskReddit"

@router.get("/generate_short_video/{subreddit}")
def generate_short_video(subreddit: SubredditEnum):
    try:
        video.generate_short_video(subreddit)
        return {"message": f"Short video successfully generated and uploaded."}
    except Exception as e:
        logger.error(f"Error generating short video: {e}")

@router.get("/get_video_data/{video_id}")
def get_video_data(video_id: str):
    try:
        video_data = video.get_video_data(video_id)
        return video_data
    except Exception as e:
        logger.error(f"Error getting video data: {e}")

@router.get('/ongoing_videos')
def get_ongoing_videos():
    try:
        ongoing_videos = video.get_ongoing_videos()
        return ongoing_videos
    except Exception as e:
        logger.error(f"Error getting ongoing videos: {e}")

@router.get('/all_videos')
def get_all_videos():
    try:
        all_videos = video.get_all_videos()
        return all_videos
    except Exception as e:
        logger.error(f"Error getting all videos: {e}")

@router.get('/delete_video/{video_id}')
def delete_video(video_id: str):
    try:
        video.delete_video(video_id)
        return {"message": "Video deleted successfully!"}
    except Exception as e:
        logger.error(f"Error deleting video: {e}")