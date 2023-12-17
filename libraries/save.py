from utils.database.schemas import __create_video_data, does_reddit_id_exist
from utils.database.models import VideosCreate
from utils.data import read_json, check_ongoing, close_the_process
from datetime import datetime

def __convert_timestamp_to_date(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')



def __get_platform_details(upload_info, platform):
    for info in upload_info:
        if info.get("platform") == platform:
            return info
    return None

def save_videos_data():
    reddit_id = check_ongoing()
    
    if does_reddit_id_exist(reddit_id):
        close_the_process()
        return
    
    reddit_details = read_json(reddit_id)

    generated_date_human_readable = __convert_timestamp_to_date(reddit_details["generated_date"])

    # Convert timestamps to human-readable format for all platforms
    for info in reddit_details["upload_info"]:
        info["upload_date"] = __convert_timestamp_to_date(info["upload_date"])

    video = VideosCreate(
        reddit_id=reddit_details["id"],
        subreddit=reddit_details["subreddit"],
        title=reddit_details["title"],
        duration=reddit_details["duration"],
        generated_data=generated_date_human_readable,
        upload_info=reddit_details["upload_info"]  # Use all upload_info details
    )
    
    close_the_process()
    __create_video_data(video)