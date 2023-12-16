from libraries.reddit import get_top_reddit_post
from libraries.screenshots import get_screenshots_of_reddit_posts
from libraries.voice import generate_voice
from utils.log import setup_logger, get_logger
from libraries.video import make_final_video
from utils.database.schemas import save_videos_data
from utils.chatgpt import get_meta_data

setup_logger()
logger = get_logger()

def __generate_short_video(subreddit):
    # logger.info(f"Getting top reddit post from: r/{subreddit}")
    # reddit_data = get_top_reddit_post(subreddit)
    
    # logger.info("Downloading screenshots of reddit posts...")
    # selected_reddit_data = get_screenshots_of_reddit_posts(reddit_data)
    # logger.info("Screenshots captured successfully!")
    
    # logger.info("Generating voice...")
    # reddit_details = generate_voice(selected_reddit_data)
    # logger.info("Generating voice completed!")
    
    # logger.info("Video Generation started...")
    # video_files = make_final_video(reddit_details)
    # logger.info("Generating video completed!")
    
    video_files = [
        {
            'id': '18itok3', 
            'generated_data': '1702681442', 
            'reddit_title': 'What is the most incredible human feat of all time?', 
            'path': 'storage/18itok3/18itok3.mp4'
         }
    ]
    
    # Generata meta tags using chatgpt
    logger.info('Generating meta tags...')
    meta_data = get_meta_data(video_files) 
    logger.info('Meta tags generated successfully!')
    
    
    # upload the video files to the youtube and tiktok

    
    # Save the video files to the database
    save_videos_data(subreddit, video_files)
    
    
def main():
    logger.info("Starting...")
    
    
    subreddits = ["AskReddit"]
    for subreddit in subreddits:
        __generate_short_video(subreddit)
    
    
    logger.info("Done.")
    
if __name__ == "__main__":
    main()