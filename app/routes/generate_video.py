from fastapi import APIRouter
from app.libraries import generate_video
from utils.log import setup_logger, get_logger

setup_logger()
logger = get_logger()


router = APIRouter(
    tags=["Generate Videos"],
)

@router.get("/")
def read_root():
    return {"message": "Hello, this is your FastAPI application!"}

@router.get("/generate_short_video/{subreddit}")
def generate_short_video(subreddit: str):
    generate_video.generate_short_video(subreddit)
    
    return {"message": f"Short video successfully generated and uploaded...."}