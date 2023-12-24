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
    video.generate_short_video(subreddit)
    
    return {"message": f"Short video successfully generated and uploaded...."}

@router.get("/get_video_data/{video_id}")
def get_video_data(video_id: str):
    video_data = video.get_video_data(video_id)
    
    return video_data

@router.get('/ongoing_videos')
def get_ongoing_videos():
    ongoing_videos = video.get_ongoing_videos()
    
    return ongoing_videos