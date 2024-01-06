from pymongo.mongo_client import MongoClient
from config import config
from motor.motor_asyncio import AsyncIOMotorClient

async def setup_db():
    config_data = config.load_configuration()
    MONGODB_USERNAME = config_data['MONGODB_USERNAME']
    MONGODB_PASSWORD = config_data['MONGODB_PASSWORD']
    MONGODB_URL = config_data['MONGODB_URL']
    
    client = AsyncIOMotorClient(
        f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_URL}/?retryWrites=true&w=majority"
    )

    db = client.NovaRedditAutoGen
    video_collection = db["video_collection"]
    
    return video_collection


