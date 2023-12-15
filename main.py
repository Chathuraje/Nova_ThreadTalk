from libraries.reddit import get_top_reddit_post
from libraries.screenshots import get_screenshots_of_reddit_posts
from libraries.voice import generate_voice
from utils.log import setup_logger, get_logger

setup_logger()
logger = get_logger()

def __generate_short_video(subreddit):
    logger.info(f"Getting top reddit post from: r/{subreddit}")
    reddit_data = get_top_reddit_post(subreddit)
    
    logger.info("Downloading screenshots of reddit posts...")
    selected_data = get_screenshots_of_reddit_posts(reddit_data)
    logger.info("Screenshots captured successfully!")
    
    logger.info("Generating voice...")
    generate_voice(selected_data)
    logger.info("Generating voice completed!")


def main():
    logger.info("Starting...")
    
    
    subreddits = ["AskReddit"]
    for subreddit in subreddits:
        __generate_short_video(subreddit)
    
    
    logger.info("Done.")
    
if __name__ == "__main__":
    main()