from fastapi import APIRouter
from app.libraries import generate_video
from utils.log import setup_logger, get_logger
from enum import Enum

setup_logger()
logger = get_logger()


router = APIRouter(
    tags=["Generate Videos"],
)

@router.get("/")
def read_root():
    return {"message": "Hello, this is your FastAPI application!"}

class SubredditEnum(str, Enum):
    AskReddit = "AskReddit"

@router.get("/generate_short_video/{subreddit}")
def generate_short_video(subreddit: SubredditEnum):
    generate_video.generate_short_video(subreddit)
    
    return {"message": f"Short video successfully generated and uploaded...."}