from libraries.reddit import get_top_reddit_post
from libraries.screenshots import get_screenshots_of_reddit_posts
from utils.log import setup_logger, get_logger

setup_logger()
logger = get_logger()

def main():
    logger.info("Starting...")
    
    subreddit = "AskReddit"
    reddit_data = get_top_reddit_post(subreddit)
    get_screenshots_of_reddit_posts(reddit_data)
    
    logger.info("Done.")
    
if __name__ == "__main__":
    main()