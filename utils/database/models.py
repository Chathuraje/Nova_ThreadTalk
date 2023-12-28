from typing import Optional, List
from pydantic import BaseModel, validator
from libraries.setup.db import setup_db
from utils.log import setup_logger, get_logger

setup_logger()
logger = get_logger()

class UploadInfo(BaseModel):
    platform: str
    url: str
    status: str
    upload_date: str


class VideosBase(BaseModel):
    __tablename__ = 'Videos'

    reddit_id: str
    subreddit: str
    title: str
    duration: int
    generated_data: str
    upload_info: Optional[List[UploadInfo]]  # Change to List[UploadInfo]

    @validator("reddit_id", pre=True, always=True)
    def check_reddit_id(cls, value):
        video_collection = setup_db()
        
        # Ensure that reddit_id is unique
        if video_collection.find_one({"reddit_id": value}):
            logger.error(f"Reddit id: {value} already exists in the database.")

        return value


class VideosCreate(VideosBase):
    upload_info: Optional[List[UploadInfo]]  # Change to List[UploadInfo]

class Videos(VideosBase):
    id: str

    class Config:
        from_attributes = True
