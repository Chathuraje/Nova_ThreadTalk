from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from .models import VideosCreate, Videos
from config.db import video_collection
from utils.data import read_json, check_ongoing, update_json



def __create_video_data(video: VideosCreate):
    video_data = video.dict()
    result = video_collection.insert_one(video_data)
    inserted_id = result.inserted_id
    
    return __get_video_data_by_id(result.inserted_id)
    
def __get_video_data_by_id(video_id: str):
    video_object_id = ObjectId(video_id)
    video_data = video_collection.find_one({"_id": video_object_id})
    
    return video_data

def __get_video_by_reddit_id(reddit_id: str):
    video_data = video_collection.find_one({"reddit_id": reddit_id})
    
    return video_data


def does_reddit_id_exist(reddit_id: str):
    existing_video = video_collection.find_one({"reddit_id": reddit_id})
    return existing_video is not None
