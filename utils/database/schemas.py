from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from .models import VideosCreate, Videos
from config.db import video_collection



def __create_video_data(video: VideosCreate):
    video_data = video.dict()
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


def save_videos_data(reddit_details):
    """
    reddit_details = {
        'id': '18j6dbr', 
        'subreddit': 'AskReddit', 
        'title': 'What was something that was done in the name of safety that turned out to be more dangerous than the hazard that it was intended to prevent?',
        'url': 'http://www.reddit.com/r/AskReddit/comments/18j6dbr/what_was_something_that_was_done_in_the_name_of/', 
        'duration': '45',
        'generated_data': 1702743649.315682, 
        'youtube_details': {
            'title': "What Went Wrong: The Dangers of Overprotective Measures – Reddit's Top Comments Compilation!", 
            'description': "Top Comment Compilation: Safety Measures Gone Wrong! Discover the most dangerous safety precautions that backfired, leaving us in more danger. From faulty seatbelts to ineffective childproofing, these stories will make you question if safety precautions are always effective. Join us as we explore the Reddit community's experiences and opinions on safety measures gone awry. Don't miss this eye-opening compilation video!", 
            'tags': 'safety hazards, dangerous safety measures, unintended consequences, safety gone wrong, safety backfires', 
            'upload_date': 1702745886.587303, 
            'url': 'https://www.youtube.com/watch?v=KUWlYm7o8TM', 
            'status': 'uploaded'
        }, 
        'tiktok_details': {
            'title': 'Disastrous Safety Measures: When Good Intentions Go Wrong', 
            'description': "Check out these shocking moments where safety measures ended up being more dangerous than the original hazards! From faulty equipment to misguided precautions, this top comment compilation exposes the surprising risks that arose in the name of safety. Don't miss out on the jaw-dropping stories and insightful discussions in this must-watch video! #SafetyGoneWrong #DangerousPrecautions #TopCommentCompilation",  
            'tags': 'reddit, topcomment, compilation, safetyhazard, dangerprevention, fails, safetyfails, irony, unintendedconsequences, dangerousdecisions, safetyfirst', 
            'upload_date': 1702745886.587303, 
            'url': '', 
            'status': ''
        }
    }
    """
    
    reddit_details["generated_data"] = datetime.utcfromtimestamp(reddit_details["generated_data"]).strftime('%Y-%m-%d %H:%M:%S')
    reddit_details["youtube_details"]["upload_date"] = datetime.utcfromtimestamp(reddit_details["youtube_details"]["upload_date"]).strftime('%Y-%m-%d %H:%M:%S')
    
    video = VideosCreate(
        reddit_id=reddit_details["id"],
        subreddit=reddit_details["subreddit"],
        title=reddit_details["title"],
        duration=reddit_details["duration"],
        generated_data=reddit_details["generated_data"],
        youtube_details=reddit_details["youtube_details"],
        tiktok_details=None
    )
    
    data = __create_video_data(video)
    
    
    return data
