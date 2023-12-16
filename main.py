from libraries.reddit import get_top_reddit_post
from libraries.screenshots import get_screenshots_of_reddit_posts
from libraries.voice import generate_voice
from utils.log import setup_logger, get_logger
from libraries.video import make_final_video
from utils.database.schemas import save_videos_data
from libraries.chatgpt import get_meta_data
from libraries.youtube import upload_to_youtube
from libraries.telegram import send_telegram_message

setup_logger()
logger = get_logger()

def __generate_short_video(subreddit):
    logger.info(f"Getting top reddit post from: r/{subreddit}")
    reddit_data = get_top_reddit_post(subreddit)
    
    logger.info("Downloading screenshots of reddit posts...")
    selected_reddit_data = get_screenshots_of_reddit_posts(reddit_data)
    logger.info("Screenshots captured successfully!")
    
    logger.info("Generating voice...")
    reddit_details = generate_voice(subreddit, selected_reddit_data)
    logger.info("Generating voice completed!")
    
    logger.info("Video Generation started...")
    reddit_details = make_final_video(reddit_details)
    logger.info("Generating video completed!")
    
    logger.info('Generating meta tags...')
    reddit_details = get_meta_data(reddit_details) 
    logger.info('Meta tags generated successfully!')
    
    logger.info("Uploading videos to YouTube...")
    reddit_details = upload_to_youtube(reddit_details)
    logger.info("Videos uploaded successfully!")
    
    logger.info("Saving data to database...")
    data = save_videos_data(reddit_details)
    logger.info("Data saved successfully!")

    # logger.info("Sending message to telegram...")
    # await send_telegram_message(data)
    # logger.info("Message sent successfully!")
    
    
    
def main():
    logger.info("Starting...")
    
    
    subreddits = ["AskReddit"]
    for subreddit in subreddits:
        __generate_short_video(subreddit)
    
    
    logger.info("Done.")
    
if __name__ == "__main__":
    main()