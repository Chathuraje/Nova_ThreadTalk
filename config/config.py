import os
import configparser
import os
from dotenv import load_dotenv


# Access config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

STAGE = config.get('Settings', 'STAGE')
VIDEO_LENGTH = int(config.get('Settings', 'VIDEO_LENGTH'))
MIN_COMMENT_WORDS = int(config.get('Settings', 'MIN_COMMENT_WORDS'))
MAX_COMMENT_WORDS = int(config.get('Settings', 'MAX_COMMENT_WORDS'))
SCREENSHOT_WIDTH = int(config.get('Settings', 'SCREENSHOT_WIDTH'))
SCREENSHOT_HEIGHT = int(config.get('Settings', 'SCREENSHOT_HEIGHT'))
COMMENT_LIMIT = int(config.get('Settings', 'COMMENT_LIMIT'))
POST_LIMIT_FOR_ONE_TIME = int(config.get('Settings', 'POST_LIMIT_FOR_ONE_TIME'))
VIDEO_WIDTH = int(config.get('Settings', 'VIDEO_WIDTH'))
VIDEO_HEIGHT = int(config.get('Settings', 'VIDEO_HEIGHT'))


# Load environment variables from .env file
load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
ELEVENLABS_API_KEYS = os.getenv("ELEVENLABS_API_KEYS").split(",")

if STAGE == "development":
    MONGODB_URL = os.getenv("MONGODB_DEVELOPMENT_URL")
    MONGODB_USERNAME = os.getenv("MONGODB_DEVELOPMENT_USERNAME")
    MONGODB_PASSWORD = os.getenv("MONGODB_DEVELOPMENT_PASSWORD")
elif STAGE == "production":
    MONGODB_URL = os.getenv("MONGODB_PRODUCTION_URL")
    MONGODB_USERNAME = os.getenv("MONGODB_PRODUCTION_USERNAME")
    MONGODB_PASSWORD = os.getenv("MONGODB_PRODUCTION_PASSWORD")