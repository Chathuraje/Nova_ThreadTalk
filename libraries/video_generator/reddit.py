import asyncpraw
import pandas as pd
from praw.models import MoreComments
from bs4 import BeautifulSoup
from markdown import markdown
import re
from utils.logger import setup_logger, get_logger
from utils.database.schemas import does_reddit_id_exist
from utils.folders import create_folders
from utils.data import create_reddit_json, update_reddit_json, check_ongoing, create_json, update_json, create_not_found_json, read_not_found_json
from config import config
from fastapi import HTTPException

setup_logger()
logger = get_logger()

async def __get_reddit_client():
    config_data = config.load_configuration()

    try:
        reddit_client = asyncpraw.Reddit(
            client_id=config_data["REDDIT_CLIENT_ID"],
            client_secret=config_data["REDDIT_CLIENT_SECRET"],
            user_agent=config_data["REDDIT_USER_AGENT"]
        )
        logger.info("Reddit client successfully created.")
        return reddit_client
    except asyncpraw.exceptions.Forbidden as e:
        logger.error(f"Error creating Reddit client: {e}")
        raise  Exception("Error creating Reddit client. Please check your credentials.")
    
def __markdown_to_text(markdown_string):
    try:
        html = markdown(markdown_string)
        html = re.sub(r'<pre>(.*?)</pre>', ' ', html)
        html = re.sub(r'<code>(.*?)</code>', ' ', html)
        html = re.sub(r'~~(.*?)~~', ' ', html)
        soup = BeautifulSoup(html, "html.parser")
        text = ''.join(soup.findAll(text=True))
        text = __remove_special_characters(text)

        return text
    
    except Exception as e:
        logger.error(f"Error converting markdown to text: {e}")
        raise Exception('Error converting markdown to text')

def __remove_special_characters(text):
    try:
        ascii_removed = re.sub(r'[^\x00-\x7F]+', '', text)
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
        unwanted_text_removed = re.sub(r'\\n', ' ', emojis_removed)
        line_breaks_removed = unwanted_text_removed.replace('\n', ' ')
        return line_breaks_removed.strip()
    
    except Exception as e:
        logger.error(f"Error removing special characters: {e}")
        raise Exception('Error removing special characters')

def __profanity_load():
    try:
        profanity_data = pd.read_csv("data/profanity_check.csv")
        profanity_words = set(profanity_data["word"].str.lower())

        return profanity_words
    
    except FileNotFoundError as e:
        logger.error(f"Error loading profanity words: {e}")
        raise HTTPException(status_code=500, detail="Error loading profanity words file")
    except Exception as e:
        logger.error(f"Error loading profanity words: {e}")
        raise Exception('Error loading profanity words')

async def __get_top_reddit_comment(reddit, post_id: str):
    MIN_COMMENT_WORDS = 5
    MAX_COMMENT_WORDS = 25 

    try:
        submission = await reddit.submission(id=post_id)
    except Exception as e:
        logger.error(f"Failed to retrieve submission with ID {post_id}: {e}")
    
    profanity_words = __profanity_load()
    data = []
    comment_list = submission.comments.list()
    for comment in comment_list:
        if isinstance(comment, MoreComments) or comment.banned_by or comment.body in ["[removed]", "[deleted]"]:
            continue
        if any(word in comment.body.lower() for word in profanity_words) or not MIN_COMMENT_WORDS < len(comment.body.split()) < MAX_COMMENT_WORDS:
            continue
        if re.search("(?P<url>https?://[^\s]+)", comment.body):
            continue
            
        comments_body = __markdown_to_text(comment.body)
        
        logger.info(f"Selected comment {comment.id} with body: {comments_body}")
        data.append({
            "id": comment.id,
            "body": comments_body,
            "url": comment.permalink
        })
        
        COMMENT_LIMIT = 5
        if len(data) == (COMMENT_LIMIT*2):
            break
        
    if len(data) == 0:
        create_not_found_json(post_id)
        logger.error("Suitable comment not found. Please try different subreddit or try again.")
        raise Exception(status_code=500, detail="Suitable comment not found. Please try different subreddit or try again.")
    
    return data

async def get_top_reddit_post(subredditName: str):
    reddit_id = check_ongoing()
    
    if reddit_id != "":
        logger.info(f"Post {reddit_id} is already in progress. Continuing...")
        return None
    
    profanity_words = __profanity_load()
    
    try:
        reddit = await __get_reddit_client()
        subreddit = await reddit.subreddit(subredditName)
    except Exception as e:
        logger.error(f"Error getting subreddit: {e}")
        raise Exception("Error getting subreddit. Please check your subreddit name.")
    
    async for post in subreddit.top(time_filter="day", limit=20):
        reddit_id = post.id
        logger.info(f"Processing post {post.id}... Title: {post.title}")
        
        if post.over_18 or post.stickied or any(word in post.title.lower() for word in profanity_words): 
            logger.info(f"Post {post.id} failed initial filters. Skipping...")
            continue
        
        if await does_reddit_id_exist(post.id):
            logger.info(f"Post {post.id} already exists in the database. Skipping...")
            continue
        
        if post.id in read_not_found_json():
            logger.info(f"Post {post.id} already exists in the not found json. Skipping...")
            continue
        

        logger.info(f"Post {post.id} passed initial filters. Processing comments...")
        
        comment_data = await __get_top_reddit_comment(reddit, post.id)
        
        if comment_data != []:
            create_folders(post.id)
            create_reddit_json(post.id)
            video_info = create_json(post.id)
            
            data = {
                "id": post.id,
                "subreddit": subredditName,
                "title": post.title,
                "url": post.url,
                "comments": comment_data
            }
            
            update_reddit_json(data)
            
            video_info['subreddit'] = subredditName
            video_info['title'] = post.title
            video_info['url'] = post.url
            update_json(video_info)
            return video_info
    
    logger.error("Suitable post not found. Please try different subreddit or try again.")
    raise Exception("Suitable post not found. Please try different subreddit or try again")
    
        