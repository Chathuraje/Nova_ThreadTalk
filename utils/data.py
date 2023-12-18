import json
from utils.log import setup_logger, get_logger
import os

setup_logger()
logger = get_logger()

def create_reddit_json(reddit_id):
    logger.info("Creating JSON file...")
    
    data = {}
    file_path = f"storage/{reddit_id}/data/reddit.json"
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=2)
        
        
def update_reddit_json(data):
    reddit_id = data['id']
    file_path = f"storage/{reddit_id}/data/reddit.json"
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
        
    ongoing = {
        "id": reddit_id
    }
    file_path = f"storage/ongoing.json"
    with open(file_path, "w") as json_file:
        json.dump(ongoing, json_file, indent=2)


def read_reddit_json(reddit_id):
    file_path = f"storage/{reddit_id}/data//reddit.json"
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        
    return data



def close_the_process():
    file_path = f"storage/ongoing.json"
    if os.path.exists(file_path):
        with open(file_path, 'w') as json_file:
            json.dump({"id": ""}, json_file)
        logger.info("File closed successfully")
    else:
        logger.info("The file does not exist")

def check_ongoing():
    file_path = f"storage/ongoing.json"
    if os.path.exists(file_path):
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            
        return data['id']
    else:
        return ""
    

def create_json(data):
    file_path = f"storage/{data['id']}/data/video.json"

    with open(file_path, 'w') as f:
        json.dump({
            'id': data['id'],
            'subreddit': data['subreddit'],
            'title': data['title'],
            'url': data['url'],
            'name': "",
            'voice': False,
            'comments': [],
            'generated_date': None,
            'duration': 0,
            'meta_tags': [],
            'upload_info': []
        }, f, indent=4)

    # Need to return the created json file
    with open(file_path, 'r') as f:
        data = json.load(f)

    return data

    

def update_json(data):
    reddit_id = data['id']
    file_path = f"storage/{reddit_id}/data/video.json"
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
        
        
def read_json(reddit_id):
    file_path = f"storage/{reddit_id}/data//video.json"
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        
    return data