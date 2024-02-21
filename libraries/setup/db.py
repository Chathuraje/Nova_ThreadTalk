from pymongo.mongo_client import MongoClient
from config import config
from motor.motor_asyncio import AsyncIOMotorClient
from utils.logger import setup_logger, get_logger

setup_logger()
logger = get_logger()

async def setup_db():
    try:
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
        
    except Exception as e:
        logger.error(f"Error connecting to the database. {e}")
    


