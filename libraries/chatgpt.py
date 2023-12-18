from openai import OpenAI
from utils.log import setup_logger, get_logger
from config.config import OPENAI_API_KEY
import time
from utils.data import read_json, check_ongoing, update_json, create_json

setup_logger()
logger = get_logger()

def initialize_openai():
    try:
        client = OpenAI(
            api_key = OPENAI_API_KEY,
        )
        
        return client
    except Exception as e:
        logger.error(f"Error initializing OpenAI: {e}")

def generate_chat_completion(client, messages):
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=100,
            temperature=0.7,
            n=1
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating GPT: {e}")
        return None

def ask_gpt(client, prompt, conversation):
    conversation.append({'role': 'system', 'content': prompt})
    conversation_response = generate_chat_completion(client, conversation)
    
    if conversation_response is None:
        # Retry after a delay if the first attempt fails
        time.sleep(20)
        conversation_response = generate_chat_completion(client, conversation)

    return conversation_response

def ask(client, prompt, conversation=[]):
    logger.info(f" Asking GPT: {prompt}")
    
    output = ask_gpt(client, prompt, conversation)
    output = output.replace('"', '')
    
    return output


def __check_if_metatags_exists(reddit):
    meta_tags = reddit["meta_tags"]
    if meta_tags == []:
        return False, False
    else:
        youtube_exists = False
        tiktok_exists = False

        for tag in meta_tags:
            if tag['platform'] == 'youtube':
                youtube_exists = True
            
            if tag['platform'] == 'tiktok':
                tiktok_exists = True

        return youtube_exists, tiktok_exists
    
    


def get_meta_data():
    reddit_id = check_ongoing()
    reddit_details = read_json(reddit_id)
    
    youtube_exists, tiktok_exists = __check_if_metatags_exists(reddit_details)
    
    if youtube_exists and tiktok_exists:
        logger.info(f"Post {reddit_id} already has meta tags. Skipping...")
        return None
    else:
        client = initialize_openai()
        video_name = reddit_details['title']

        if not youtube_exists:
            logger.info(f"Generating meta tags for YouTube...")
            youtube_details = __get_meta_data(client, video_name, platform='youtube')
            reddit_details['meta_tags'].append(youtube_details)

        # if not tiktok_exists:
        #     logger.info(f"Generating meta tags for TikTok...")
        #     tiktok_details = __get_meta_data(client, video_name, platform='tiktok')
        #     reddit_details['meta_tags'].append(tiktok_details)

        update_json(reddit_details)
    
    

def __get_meta_data(client, video_name, platform):

    if platform == 'youtube':
        title_prompt_type = 'title'
        description_prompt_type = 'description'
        tags_prompt_type = 'tags'
        additional = 'Include relevant keywords for YouTube SEO.'
        
        logger.info("Generating meta data for YouTube...")
    elif platform == 'tiktok':
        title_prompt_type = 'caption'
        description_prompt_type = 'description'
        tags_prompt_type = 'hashtags'
        additional = 'Keep it short and engaging for TikTok audience.'
        
        logger.info("Generating meta data for TikTok...")
    else:
        logger.error("Invalid platform. Supported platforms are 'youtube' and 'tiktok'.")
        
    # Generate title
    title_prompt = f"Create a {title_prompt_type} for a reddit top comment compilation video about {video_name}. {additional}. only one is allowed. do not add additional text or data"
    title_output = ask(client, title_prompt)
    logger.info(f"Title: {title_output}")

    # Generate description
    description_prompt = f"Write a {description_prompt_type} for a reddit top comment compilation video about {video_name}. {additional}. only one description is allowed. do not add additional text or data, limite use less than 100 words"
    description_output = ask(client, description_prompt)
    logger.info(f"Description: {description_output}")
    
    # Generate tags/hashtags
    tags_prompt = f"Suggest {tags_prompt_type} for a reddit top comment compilation video about {video_name}. {additional}, do not add # sign. seperate each tag with a comma."
    tags_output = ask(client, tags_prompt)
    logger.info(f"Tags: {tags_output}")
    
    meta_data = {
        'platform': platform,
        'title': title_output,
        'description': description_output,
        'tags': tags_output
    }

    return meta_data
    