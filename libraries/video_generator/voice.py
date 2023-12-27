from elevenlabs import Voice, VoiceSettings, generate, set_api_key, play
from pathlib import Path
from utils.log import setup_logger, get_logger
from elevenlabs.api import User
from utils.data import read_json, check_ongoing, update_json
from gtts import gTTS
from config import config

setup_logger()
logger = get_logger()

def __set_api_key(characters):
    config_data = config.load_configuration()
    
    for key in config_data['ELEVENLABS_API_KEYS']:
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
    config_data = config.load_configuration()
    
    try:
        if config_data['STAGE'] == "DEVELOPMENT":
            tts = gTTS(text=text, lang='en')
            tts.save(f"{voice_folder}/{name}.mp3")
        elif config_data['STAGE'] == "PRODUCTION":
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
                    
        return True
    except Exception as e:
        logger.error(f"Error generating audio for {name}: {e}")
        
        
        

def __count_characters(reddit_data):
    title_characters_count = 0
    comments_characters_count = 0

    # Count characters in the title only if 'voice' is false
    if not reddit_data['voice']:
        title_characters_count = len(reddit_data['title'])

    # Count characters in comments only if 'voice' is false for each comment
    for comment in reddit_data['comments']:
        if not comment['voice']:
            comments_characters_count += len(comment['text'])

    total_characters_count = title_characters_count + comments_characters_count

    return total_characters_count


def __check_is_voice_available(reddit_selected):
    if any(comment.get("voice", False) is False for comment in reddit_selected["comments"]):
        return True
    else:
        return False

def generate_voice():
    reddit_id = check_ongoing()
    reddit_selected = read_json(reddit_id)
    
    if __check_is_voice_available(reddit_selected):
        logger.info("Voice not generated for all comments. Generating voice...")
    else:
        logger.info("Voice already generated for all. Skipping...")
        return
    
    characters = __count_characters(reddit_selected)
    logger.info(f"Generating voice for {reddit_selected['id']} with {characters} characters.")
    
    logger.info("ELEVENLABS: Connecting API")
    success = __set_api_key(characters)

    if not success:
        logger.error("All API keys failed. Unable to set a valid API key.")
        exit()
        
    reddit_id = reddit_selected['id']
        
    name = reddit_selected['name']
    title = reddit_selected['title']
    comments = reddit_selected['comments']
    voice = reddit_selected['voice']

    if voice:
        logger.info("Voice already generated. Skipping...")
    else:
        if __generate_audio(reddit_id, name, title):
            reddit_selected['voice'] = True

    # Loop through the comments list
    for comment in comments:
        comment_id = comment['id']
        comment_name = comment['name']
        comment_text = comment['text']
        comment_voice = comment['voice']
        
        if comment_voice:
            logger.info(f"Voice already generated for {comment_id}. Skipping...")
            continue
        else:
            if __generate_audio(reddit_id, comment_name, comment_text, comment_id):
                comment['voice'] = True
            
    update_json(reddit_selected)