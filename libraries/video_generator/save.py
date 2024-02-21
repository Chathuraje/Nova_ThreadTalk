from utils.database.schemas import __create_video_data, does_reddit_id_exist, __get_video_by_reddit_id
from utils.database.models import VideosCreate
from utils.data import read_json, check_ongoing, close_the_process
from utils.time import format_sri_lankan_time

async def save_videos_data():
    reddit_id = check_ongoing()
    
    exists = await does_reddit_id_exist(reddit_id)
    if exists:
        close_the_process()
        return await __get_video_by_reddit_id(reddit_id)
    
    reddit_details = read_json(reddit_id)

    generated_date_human_readable = format_sri_lankan_time(reddit_details["generated_date"])

    # Convert timestamps to human-readable format for all platforms
    for info in reddit_details["upload_info"]:
        info["upload_date"] = format_sri_lankan_time(info["upload_date"])

    video = VideosCreate(
        reddit_id=reddit_details["id"],
        subreddit=reddit_details["subreddit"],
        title=reddit_details["title"],
        duration=reddit_details["duration"],
        generated_data=generated_date_human_readable,
        upload_info=reddit_details["upload_info"]  # Use all upload_info details
    )
    
    data = await __create_video_data(video)
    close_the_process()
    
    return data