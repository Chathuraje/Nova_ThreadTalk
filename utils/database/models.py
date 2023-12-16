from typing import Optional, Dict
from pydantic import BaseModel, validator
from config.db import video_collection
from utils.log import setup_logger, get_logger

setup_logger()
logger = get_logger()


class TikTokDetails(BaseModel):
    title: str
    description: str
    tag: str
    upload_date: str
    url: str
    status: str

class YouTubeDetails(BaseModel):
    title: str
    description: str
    tag: str
    upload_date: str
    url: str
    status: str

class VideosBase(BaseModel):
    __tablename__ = 'Videos'
    
    reddit_id: str
    subreddit: str
    reddit_title: str
    generated_data: str
    youtube_details: Optional[TikTokDetails]
    tiktok_details: Optional[YouTubeDetails]
    status: str
    
    @validator("reddit_id", pre=True, always=True)
    def check_reddit_id(cls, value):
        # Ensure that reddit_id is unique
        if video_collection.find_one({"reddit_id": value}):
            logger.error(f"Reddit id: {value} already exists in the database.")
            
        return value

class VideosCreate(VideosBase):
    tiktok_details: Optional[TikTokDetails]
    youtube_details: Optional[YouTubeDetails]

class Videos(VideosBase):
    id: str

    class Config:
        from_attributes = True
        

