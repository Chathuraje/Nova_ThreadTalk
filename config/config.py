import configparser
import json
import os

def load_configuration():
    config = configparser.ConfigParser()
    config.read('config.ini')
    STAGE = config.get('Settings', 'STAGE')
    
    
    FILE_PATH = 'secrets/secrets.json'
    with open(FILE_PATH, 'r') as config_file:
        config_data = json.load(config_file)

    configuration = {
        "STAGE": STAGE,
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
    config_file = 'config.ini'

    if not os.path.exists(config_file):
        config['Settings'] = {'STAGE': 'default_stage'}

    config.read(config_file)

    config['Settings']['STAGE'] = changed_mode

    with open(config_file, 'w') as configfile:
        config.write(configfile)

    return changed_mode


def get_mode():
    config = configparser.ConfigParser()
    config_file = 'config.ini'

    config.read(config_file)

    return config['Settings']['STAGE']


    
    