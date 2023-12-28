from libraries.video_generator import reddit
from libraries.video_generator import screenshots
from libraries.video_generator import voice
from libraries.video_generator import video
from libraries.video_generator import chatgpt
from libraries.video_generator import save
from libraries.upload import youtube
from libraries.upload import tiktok
from utils import storage
from libraries.video_generator import telegram
from utils.log import setup_logger, get_logger
from utils import data
import time

setup_logger()
logger = get_logger()

def get_reddit_post(subreddit):
    try:
        logger.info(f"Getting top reddit post from: r/{subreddit}")
        reddit.get_top_reddit_post(subreddit)
        logger.info(f"Got top reddit post from: r/{subreddit} successfully!")
        return True
    
    except Exception as e:
        logger.error(f"Error getting Reddit post: {e}")
        return False

def capture_screenshots():
    try:
        logger.info("Downloading screenshots of Reddit posts...")
        screenshots.get_screenshots_of_reddit_posts()
        logger.info("Screenshots captured successfully!")
        return True
    except Exception as e:
        logger.error(f"Error capturing screenshots: {e}")
        return False

def generate_voice_over():
    try:
        logger.info("Generating voice...")
        voice.generate_voice()
        logger.info("Voice generated successfully!")
        return True
    except Exception as e:
        logger.error(f"Error generating voice: {e}")
        return False

def create_video():
    try:
        logger.info("Video Generation started...")
        video.make_final_video()
        logger.info("Video generated successfully!")
        return True
    except Exception as e:
        logger.error(f"Error generating video: {e}")
        return False

def generate_meta_tags():
    try:
        logger.info('Generating meta tags...')
        chatgpt.get_meta_data() 
        logger.info('Meta tags generated successfully!')
        return True
    except Exception as e:
        logger.error(f"Error generating meta tags: {e}")
        return False
    
def upload_to_youtube():
    try:
        logger.info("Uploading video to YouTube...")
        response = youtube.upload_to_youtube()
        if response != -1:
            logger.info("Video uploaded successfully!")
            return True
        else:
            global TRIES
            TRIES = -1
            logger.error("Video uploaded failed!: Quota exceeded")
            return False
    except Exception as e:
        logger.warning(f"Error uploading video: {e}")
        return False

def upload_to_tiktok():
    try:
        logger.info("Uploading video to TikTok...")
        tiktok.upload_to_tikTok()
        logger.info("Video uploaded to TikTok successfully!")
        return True
    except Exception as e:
        logger.error(f"Error uploading video to TikTok: {e}")
        return False

def save_video_data():
    try:
        logger.info("Saving data to database...")
        data = save.save_videos_data()
        logger.info("Data saved successfully!")
        return data
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        return None

def send_telegram_message(data):
    try:
        logger.info("Sending message to Telegram...")
        telegram.send_telegram_message(data)
        logger.info("Message sent to Telegram successfully!")
        return True
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
        return False
    
    

MAX_TRIES = 5
TRIES = 0


def generate_short_video(subreddit="AskReddit"):
    global TRIES
    TRIES += 1

    if not get_reddit_post(subreddit):
        return retry_on_failure(subreddit)

    if not capture_screenshots():
        return retry_on_failure(subreddit)

    if not generate_voice_over():
        return retry_on_failure(subreddit)

    if not create_video():
        return retry_on_failure(subreddit)

    if not generate_meta_tags():
        return retry_on_failure(subreddit)

    if not upload_to_youtube():
        return retry_on_failure(subreddit)
    
    # if not upload_to_tiktok():
    #     return retry_on_failure(subreddit)

    # data = save_video_data()
    # if data is None:
    #     return retry_on_failure(subreddit)

    # if not send_telegram_message(data):
    #     return retry_on_failure(subreddit)

    logger.info("Complete video creation and distribution process finished successfully!")


def retry_on_failure(subreddit):
    global TRIES
    if TRIES == -1:
        logger.fatal(f"Error. Aborting operation.")
        
    if TRIES >= MAX_TRIES:
        logger.fatal(f"Maximum retries reached. Aborting operation.")
        
    logger.info(f"Retry {TRIES}/{MAX_TRIES} in 10 seconds...")
    time.sleep(10)
    generate_short_video(subreddit) 



    
def get_video_data(video_id):
    logger.info("Getting video data...")
    video_data = data.read_json(video_id)
    logger.info("Data retrieved successfully!")
    
    return video_data


def get_ongoing_videos():
    logger.info("Getting ongoing videos...")
    ongoing_videos = data.check_ongoing()
    logger.info("Ongoing videos retrieved successfully!")
    
    return ongoing_videos

def get_all_videos():
    logger.info("Getting all videos...")
    all_videos = storage.read_all_videos()
    logger.info("All videos retrieved successfully!")
    
    return all_videos

def delete_video(video_id):
    logger.info("Deleting video...")
    storage.delete_video_folder(video_id)
    logger.info("Video deleted successfully!")
    
    return {"message": "Video deleted successfully!"}