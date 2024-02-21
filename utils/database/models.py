from typing import Optional, List
from pydantic import BaseModel, validator
from libraries.setup.db import setup_db
from utils.logger import setup_logger, get_logger

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

class VideosCreate(VideosBase):
    upload_info: Optional[List[UploadInfo]]  # Change to List[UploadInfo]

class Videos(VideosBase):
    id: str

    class Config:
        from_attributes = True
