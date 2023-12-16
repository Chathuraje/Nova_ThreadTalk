from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from .models import VideosCreate, Videos
from config.db import video_collection



def __create_video_data(video: VideosCreate):
    video_data = video.dict()
    video_data["generated_data"] = datetime.fromtimestamp(int(video_data['generated_data']))
    result = video_collection.insert_one(video_data)
    inserted_id = result.inserted_id
    
    return __get_video_data_by_id(result.inserted_id)
    
def __get_video_data_by_id(video_id: str):
    video_object_id = ObjectId(video_id)
    video_data = video_collection.find_one({"_id": video_object_id})
    
    return video_data


def does_reddit_id_exist(reddit_id: str):
    existing_video = video_collection.find_one({"reddit_id": reddit_id})
    return existing_video is not None


def save_videos_data(subreddit, video_files):
    for video_file in video_files:
        video_create_data = VideosCreate(
            reddit_id=video_file['id'],
            subreddit=subreddit,
            reddit_title=video_file['reddit_title'],
            generated_data=video_file['generated_data'],
            status="Generated",
            tiktok_details=None,
            youtube_details=None
        )
        __create_video_data(video_create_data)
    
    return None
