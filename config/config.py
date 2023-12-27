import configparser
import json
import os
from utils.log import setup_logger, get_logger


setup_logger()
logger = get_logger()

def load_configuration():
    FILE_PATH = 'secrets/secrets.json'
    
    if not os.path.exists(FILE_PATH):
        logger.error(f"File not found: {FILE_PATH}")
    
    with open('secrets/secrets.json', 'r') as config_file:
        config_data = json.load(config_file)
        
    STAGE = config_data['STAGE']

    # Assign configurations based on the STAGE
    configuration = {
        "STAGE": config_data["stage"],
        "REDDIT_CLIENT_ID": config_data["reddit"]["client_id"],
        "REDDIT_CLIENT_SECRET": config_data["reddit"]["client_secret"],
        "REDDIT_USER_AGENT": config_data["reddit"]["user_agent"],
        "REDDIT_USERNAME": config_data["reddit"]["username"],
        "REDDIT_PASSWORD": config_data["reddit"]["password"],
        "ELEVENLABS_API_KEYS": config_data["elevenlabs"]["api_keys"],
        "OPENAI_API_KEY": config_data["openai"]["api_key"],
        "TELEGRAM_BOT_TOKEN": config_data["telegram"]["bot_token"],
    }

    if STAGE == "DEVELOPMENT":
        configuration.update({
            "MONGODB_URL": config_data["mongodb"]["development"]["url"],
            "MONGODB_USERNAME": config_data["mongodb"]["development"]["username"],
            "MONGODB_PASSWORD": config_data["mongodb"]["development"]["password"],
            "TELEGRAM_CHANNEL_ID": config_data["telegram"]["development_channel_id"],
        })
    elif STAGE == "PRODUCTION":
        configuration.update({
            "MONGODB_URL": config_data["mongodb"]["production"]["url"],
            "MONGODB_USERNAME": config_data["mongodb"]["production"]["username"],
            "MONGODB_PASSWORD": config_data["mongodb"]["production"]["password"],
            "TELEGRAM_CHANNEL_ID": config_data["telegram"]["production_channel_id"],
        })

    return configuration

def set_mode(changed_mode):
    config = configparser.ConfigParser()
    config.read('config.ini')
    config['Settings']['STAGE'] = changed_mode
    
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    
    return changed_mode



    
    