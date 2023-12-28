from openai import OpenAI
from utils.logger import setup_logger, get_logger
from utils.data import read_json, check_ongoing, update_json
from config import config

setup_logger()
logger = get_logger()

def initialize_openai():
    config_data = config.load_configuration()

    try:
        client = OpenAI(
            api_key = config_data['OPENAI_API_KEY'],
        )
        
        return client
    except Exception as e:
        logger.error(f"Error initializing OpenAI: {e}")

def generate_chat_completion(client, messages):
    config_data = config.load_configuration()
    
    if config_data['STAGE'] == "DEVELOPMENT":
        return "This is a development message.", False
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=100,
            temperature=0.7,
            n=1
        )
        
        response = completion.choices[0].message.content
        is_done = completion.choices[0].finish_reason != 'stop'
        return response, is_done

    except Exception as e:
        logger.error(f"Error generating GPT: {e}")
        return None

def ask_gpt(client, prompt, conversation):
    conversation.append({'role': 'system', 'content': prompt})
    response, is_done = generate_chat_completion(client, conversation)
    
    return response, is_done

def ask(client, prompt, conversation=[]):
    response = None
    is_done = True
    
    while response is None or is_done:
        logger.info(f"Waiting for conversation...")
        response, is_done = ask_gpt(client, prompt, conversation)
    
    output = response.replace('"', '')
    
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
    title_prompt = f"Create a {title_prompt_type} for a reddit top comment compilation video about {video_name}. {additional}. only one is allowed. do not add additional text or data. and please limit chracter count to 100 including spaces."
    title_output = ask(client, title_prompt)
    
    if len(title_output) > 100:
        logger.error("Title output is more than 100 characters.")
        
    if title_output == title_prompt:
        logger.error("Title output is same as title prompt.")
    
    logger.info(f"Title: {title_output}")

    # Generate description
    description_prompt = f"Write a {description_prompt_type} for a reddit top comment compilation video about {video_name}. {additional}. only one description is allowed. do not add additional text or data, do not add any extra context and do not add keywords. specially do not add any additional links. and please limit chracter count to 500 including spaces."
    description_output = ask(client, description_prompt)
    logger.info(f"Description: {description_output}")
    
    if description_output == description_prompt:
        logger.error("Description output is same as description prompt.")
    
    # Generate tags/hashtags
    tags_prompt = f"Suggest {tags_prompt_type} for a reddit top comment compilation video about {video_name}. {additional}, do not add # sign. seperate each tag with a comma. do not add anything like SEO, YOUTUBE, TIKTOK, SEO TITLE"
    tags_output = ask(client, tags_prompt)
    logger.info(f"Tags: {tags_output}")
    
    meta_data = {
        'platform': platform,
        'title': title_output,
        'description': description_output,
        'tags': tags_output
    }

    return meta_data
    