from elevenlabs import Voice, VoiceSettings, generate, set_api_key, play
from pathlib import Path
from utils.log import setup_logger, get_logger
from elevenlabs.api import User
from config.config import ELEVENLABS_API_KEYS
import re

setup_logger()
logger = get_logger()

def __set_api_key(characters):
    for key in ELEVENLABS_API_KEYS:
        if __set_api_key_and_check(key, characters):
            return True
    return False

def __set_api_key_and_check(key, characters):
    try:
        set_api_key(key)
        user = User.from_api()
        
        character_count = user.subscription.character_count
        character_limit = user.subscription.character_limit
        
        if character_limit - character_count >= (characters+25):
            logger.info(f"API key set successfully!: character_limit={character_limit}, character_count={character_count}")
            return True
        else:
            logger.warning("API key set but character limit is low. Trying another key.")
    except Exception as e:
        logger.error(f"Error setting API key: {e}")

    return False


def __generate_audio(reddit_id, name, text, comment_id=None):
    voice_folder = Path(f"storage/{reddit_id}/voice")
    
    try:
        audio = generate(
            text=text,
            voice=Voice(
                voice_id='TxGEqnHWrfWFTfGW9XjX',
                settings=VoiceSettings(stability=0, similarity_boost=0)
            )
        )

        with open(f"{voice_folder}/{name}.mp3", 'wb') as f:
            f.write(audio)
            
            if comment_id is not None:
                logger.info(f"Audio generated for {comment_id}")
            else:
                logger.info(f"Audio generated for {name}")
    except Exception as e:
        logger.error(f"Error generating audio for {name}: {e}")
        

def __count_characters(reddit_data):
    
    title_characters_count = len(reddit_data['title'])
    comments_characters_count = sum(len(comment['text']) for comment in reddit_data['comments'])

    total_characters_count = title_characters_count + comments_characters_count
    
    return int(total_characters_count)


def generate_voice(subreddit, reddit_data):
    characters = __count_characters(reddit_data)
    logger.info(f"Generating voice for {reddit_data['id']} with {characters} characters.")
    
    logger.info("ELEVENLABS: Connecting API")
    success = __set_api_key(characters)

    if not success:
        logger.error("All API keys failed. Unable to set a valid API key.")
        exit()
        
    reddit_id = reddit_data['id']
        
    name = reddit_data['name']
    title = reddit_data['title']
    comments = reddit_data['comments']

    voice_folder = Path(f"storage/{reddit_id}/voice")
    voice_folder.mkdir(parents=True, exist_ok=True)

    __generate_audio(reddit_id, name, title)

    # Loop through the comments list
    for comment in comments:
        comment_id = comment['id']
        comment_name = comment['name']
        comment_text = comment['text']
        __generate_audio(reddit_id, comment_name, comment_text, comment_id)
            
    data = {
        'id': reddit_id,
        'subreddit': subreddit,
        'title': title
    }
        
    return data