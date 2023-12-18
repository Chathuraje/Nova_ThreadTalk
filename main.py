from libraries.reddit import get_top_reddit_post
from libraries.screenshots import get_screenshots_of_reddit_posts
from libraries.voice import generate_voice
from utils.log import setup_logger, get_logger
from libraries.video import make_final_video
from libraries.chatgpt import get_meta_data
from libraries.save import save_videos_data
from libraries.youtube import upload_to_youtube
from libraries.telegram import send_telegram_message
from config.config import STAGE

setup_logger()
logger = get_logger()

def __generate_short_video(subreddit):
    logger.info(f"Getting top reddit post from: r/{subreddit}")
    get_top_reddit_post(subreddit)
    
    logger.info("Downloading screenshots of reddit posts...")
    get_screenshots_of_reddit_posts()
    logger.info("Screenshots captured successfully!")
    
    logger.info("Generating voice...")
    generate_voice()
    logger.info("Generating voice completed!")
    
    logger.info("Video Generation started...")
    make_final_video()
    logger.info("Generating video completed!")
    
    logger.info('Generating meta tags...')
    get_meta_data() 
    logger.info('Meta tags generated successfully!')
    
    logger.info("Uploading videos to YouTube...")
    upload_to_youtube()
    logger.info("Videos uploaded successfully!")
    
    logger.info("Saving data to database...")
    data =save_videos_data()
    logger.info("Data saved successfully!")

    logger.info("Sending message to telegram...")
    send_telegram_message(data)
    logger.info("Message sent successfully!")
    
    
    
def main():
    if STAGE == "DEVELOPMENT":
        logger.fatal(f"Starting...: MODE - {STAGE}") 
    elif STAGE == "PRODUCTION":
        logger.info(f"Starting...: MODE - {STAGE}")
    
    
    subreddits = ["AskReddit"]
    for subreddit in subreddits:
        __generate_short_video(subreddit)
    
    
    if STAGE == "DEVELOPMENT":
        logger.fatal("Done.")
    if STAGE == "PRODUCTION":
        logger.info("Done.")
    
if __name__ == "__main__":
    main()