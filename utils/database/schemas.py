from bson import ObjectId
from .models import VideosCreate
from libraries.setup.db import setup_db




async def __create_video_data(video: VideosCreate):
    video_collection = await setup_db()
    
    video_data = video.dict()
    result = await video_collection.insert_one(video_data)
    inserted_id = result.inserted_id
    
    return await __get_video_data_by_id(result.inserted_id)
    
async def __get_video_data_by_id(video_id: str):
    video_collection = await setup_db()
    
    video_object_id = ObjectId(video_id)
    video_data = await video_collection.find_one({"_id": video_object_id})
    
    return video_data

async def __get_video_by_reddit_id(reddit_id: str):
    video_collection = await setup_db()
    
    video_data = await video_collection.find_one({"reddit_id": reddit_id})
    
    return video_data


async def does_reddit_id_exist(reddit_id: str):
    video_collection = await setup_db()
    
    existing_video = await video_collection.find_one({"reddit_id": reddit_id})
    
    return existing_video is not None
