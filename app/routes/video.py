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