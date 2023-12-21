from libraries.video_generator import reddit
from libraries.video_generator import screenshots
from libraries.video_generator import voice
from libraries.video_generator import video
from libraries.video_generator import chatgpt
from libraries.video_generator import save
from libraries.upload import youtube
from libraries.upload import tiktok
from libraries.video_generator import telegram
from utils.log import setup_logger, get_logger

setup_logger()
logger = get_logger()

def generate_short_video(subreddit):  
    logger.info("Starting short video generation...")
      
    logger.info(f"Getting top reddit post from: r/{subreddit}")
    reddit.get_top_reddit_post(subreddit)
    logger.info("Reddit post captured successfully!")
    
    logger.info("Downloading screenshots of reddit posts...")
    screenshots.get_screenshots_of_reddit_posts()
    logger.info("Screenshots captured successfully!")
    
    logger.info("Generating voice...")
    voice.generate_voice()
    logger.info("Generating voice completed!")
    
    logger.info("Video Generation started...")
    video.make_final_video()
    logger.info("Generating video completed!")
    
    logger.info('Generating meta tags...')
    chatgpt.get_meta_data() 
    logger.info('Meta tags generated successfully!')
    
    logger.info("Uploading videos to YouTube...")
    youtube.upload_to_youtube()
    logger.info("Videos uploaded successfully!")
    
    logger.info("Uploading videos to TikTok")
    tiktok.upload_to_tikTok()
    logger.info("Videos uploaded successfully!")
    
    # logger.info("Saving data to database...")
    # data = save.save_videos_data()
    # logger.info("Data saved successfully!")

    # logger.info("Sending message to telegram...")
    # telegram.send_telegram_message(data)
    # logger.info("Message sent successfully!")   
    
    
    logger.info("Waiting for next video...")