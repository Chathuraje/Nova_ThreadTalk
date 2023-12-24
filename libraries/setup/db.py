from pymongo.mongo_client import MongoClient
from config.config import MONGODB_URL, MONGODB_PASSWORD, MONGODB_USERNAME

client = MongoClient(f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_URL}/?retryWrites=true&w=majority")

db = client.NovaRedditAutoGen

video_collection = db["video_collection"]

