import praw, prawcore
import pandas as pd
from praw.models import MoreComments
from bs4 import BeautifulSoup
from markdown import markdown
import re
import re
from config.config import MAX_COMMENT_WORDS, MIN_COMMENT_WORDS, COMMENT_LIMIT, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
from utils.log import setup_logger, get_logger
from utils.database.schemas import does_reddit_id_exist


setup_logger()
logger = get_logger()

def __get_reddit_client():
    """
    Get a Reddit client instance.

    Returns:
        praw.Reddit: Reddit client instance
    """
    try:
        reddit_client = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        logger.info("Reddit client successfully created.")
        return reddit_client
    except prawcore.exceptions.Forbidden as e:
        logger.error(f"Error creating Reddit client: {e}")
        raise  # You might want to handle this exception appropriately or log it and continue
    
def __markdown_to_text(markdown_string):
    """
    Converts a markdown string to plaintext.

    Args:
        markdown_string (str): Input markdown string.

    Returns:
        str: Plain text converted from markdown.
    """
    try:
        # Convert markdown to HTML
        html = markdown(markdown_string)

        # Remove code snippets
        html = re.sub(r'<pre>(.*?)</pre>', ' ', html)
        html = re.sub(r'<code>(.*?)</code>', ' ', html)
        html = re.sub(r'~~(.*?)~~', ' ', html)

        # Extract text using BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        text = ''.join(soup.findAll(text=True))

        # Remove special characters
        text = __remove_special_characters(text)

        return text
    except Exception as e:
        logger.error(f"Error converting markdown to text: {e}")
        raise  # You might want to handle this exception appropriately or log it and continue

def __remove_special_characters(text):
    """
    Removes special characters from a text.

    Args:
        text (str): Input text.

    Returns:
        str: Text with special characters removed.
    """
    try:
        # Remove ASCII characters
        ascii_removed = re.sub(r'[^\x00-\x7F]+', '', text)

        # Remove emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # Emoticons
            "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
            "\U0001F680-\U0001F6FF"  # Transport & Map Symbols
            "\U0001F700-\U0001F77F"  # Alchemical Symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE,
        )
        emojis_removed = emoji_pattern.sub(r'', ascii_removed)

        # Remove unwanted text
        unwanted_text_removed = re.sub(r'\\n', ' ', emojis_removed)
        # Replace line breaks with spaces
        line_breaks_removed = unwanted_text_removed.replace('\n', ' ')

        return line_breaks_removed.strip()
    except Exception as e:
        logger.error(f"Error removing special characters: {e}")
        raise  # You might want to handle this exception appropriately or log it and continue

def __profanity_load():
    # Load profanity data for filtering
    profanity_data = pd.read_csv("data/profanity_check.csv")
    profanity_words = set(profanity_data["word"].str.lower())

    return profanity_words

def __get_top_reddit_comment(reddit, post_id: str):
    try:
        submission = reddit.submission(id=post_id)
    except Exception as e:
        logger.error(f"Failed to retrieve submission with ID {post_id}: {e}")
        return None
    
    profanity_words = __profanity_load()
    data = []
    for comment in submission.comments.list():
        if isinstance(comment, MoreComments) or comment.banned_by or comment.body in ["[removed]", "[deleted]"]:
            continue
        if any(word in comment.body.lower() for word in profanity_words) or not MIN_COMMENT_WORDS < len(comment.body.split()) < MAX_COMMENT_WORDS:
            continue
            
        comments_body = __markdown_to_text(comment.body)
        
        logger.info(f"Selected comment {comment.id} with body: {comments_body}")
        data.append({
            "comment_id": comment.id,
            "body": comments_body,
            "comment_url": comment.permalink
        })
        
        if len(data) == (COMMENT_LIMIT*2):
            break
    
    return data

def get_top_reddit_post(subreddit: str):
    
    profanity_words = __profanity_load()
    
    try:
        # Get the Reddit client
        reddit = __get_reddit_client()
        subreddit = reddit.subreddit(subreddit)
    except Exception as e:
        pass
    
    posts = subreddit.top(time_filter="day", limit=20)
    
    # Iterate through the posts and filter based on user preferences
    for post in posts:
        logger.info(f"Processing post {post.id}... Title: {post.title}")
        
        if post.over_18 or post.stickied or any(word in post.title.lower() for word in profanity_words): 
            logger.info(f"Post {post.id} failed initial filters. Skipping...")
            continue
        
        if does_reddit_id_exist(post.id):
            logger.info(f"Post {post.id} already exists in the database. Skipping...")
            continue

        logger.info(f"Post {post.id} passed initial filters. Processing comments...")
        
        comment_data = __get_top_reddit_comment(reddit, post.id)
        
        data = {
            "id": post.id,
            "title": post.title,
            "url": post.url,
            "comments": comment_data
        }
                
        return data