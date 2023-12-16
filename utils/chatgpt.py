import openai
from utils.log import setup_logger, get_logger
from config.config import OPENAI_API_KEY
import time

setup_logger()
logger = get_logger()

def initialize_openai():
    try:
        openai.api_key = OPENAI_API_KEY
    except Exception as e:
        logger.error(f"Error initializing OpenAI: {e}")

def generate_chat_completion(messages):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            n=1
        )
        return response.choices[0].message
    except Exception as e:
        logger.error(f"Error generating GPT: {e}")
        return None

def ask_gpt(prompt, conversation):
    conversation.append({'role': 'system', 'content': prompt})
    conversation_response = generate_chat_completion(conversation)
    
    if conversation_response is None:
        # Retry after a delay if the first attempt fails
        time.sleep(20)
        conversation_response = generate_chat_completion(conversation)

    return conversation_response

def ask(prompt, conversation=[]):
    initialize_openai()
    logger.info(f" Asking GPT: {prompt}")
    
    output = ask_gpt(prompt, conversation)
    return output['content'].strip() if output else None



def get_meta_data(video_files):
    result_data = []

    for video_file in video_files:
        video_name = video_file['reddit_title']
        video_id = video_file['id']

        logger.info(f"Generating meta data for video: {video_name}")
        youtube_meta_data = __get_meta_data(video_name, platform='youtube')
        tiktok_meta_data = __get_meta_data(video_name, platform='tiktok')

        video_data = {
            'id': video_id,
            'youtube_meta_data': youtube_meta_data,
            'tiktok_meta_data': tiktok_meta_data
        }

        result_data.append(video_data)

    return result_data
    
    
    

def __get_meta_data(video_name, platform):
    meta_data_list = []

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
    title_prompt = f"Create a {title_prompt_type} for a video about {video_name}. {additional}"
    title_output = ask(title_prompt)
    logger.info(f"Title: {title_output}")

    # Generate description
    description_prompt = f"Write a {description_prompt_type} for a video about {video_name}. {additional}"
    description_output = ask(description_prompt)
    logger.info(f"Description: {description_output}")
    
    # Generate tags/hashtags
    tags_prompt = f"Suggest {tags_prompt_type} for a video about {video_name}. {additional}"
    tags_output = ask(tags_prompt)
    logger.info(f"Tags: {tags_output}")
    
    meta_data = {
        'title': title_output,
        'description': description_output,
        'tags': tags_output
    }
    meta_data_list.append(meta_data)

    return meta_data_list
    