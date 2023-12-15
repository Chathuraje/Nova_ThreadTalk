from libraries.reddit import get_top_reddit_post
from libraries.screenshots import get_screenshots_of_reddit_posts


def main():
    subreddit = "AskReddit"
    
    reddit_data = get_top_reddit_post(subreddit)
    get_screenshots_of_reddit_posts(reddit_data)
    
if __name__ == "__main__":
    main()