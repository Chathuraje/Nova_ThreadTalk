from utils.logger import setup_logger, get_logger
from datetime import datetime
from utils.data import read_json
import requests
from config import config

setup_logger()
logger = get_logger()


def create_message(reddit_details):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    heading = f"📰 Generated YouTube Short Details: {current_time}\n"
    title = f"🔍 {reddit_details['title']} \n"
    subreddit = f"🌐 Subreddit: r/{reddit_details['subreddit']}"
    duration = f"⏳ Duration: {reddit_details['duration']} seconds"
    generated_data = f"📅 Generated Data: {reddit_details['generated_data']}"
    
    # Extract YouTube and TikTok details
    youtube_details = next((data for data in reddit_details.get('upload_info', []) if data['platform'] == 'youtube'), None)
    tiktok_details = next((data for data in reddit_details.get('upload_info', []) if data['platform'] == 'tiktok'), None)
    
    # Extract YouTube and TikTok details from JSON data
    json_youtube_details = next((data for data in read_json(reddit_details['reddit_id'])['meta_tags'] if data['platform'] == 'youtube'), None)
    json_tiktok_details = next((data for data in read_json(reddit_details['reddit_id'])['meta_tags'] if data['platform'] == 'tiktok'), None)

    # Build YouTube section
    youtube_section = ""
    if youtube_details:
        youtube_section = (
            f"\n\n🎬 YouTube Video Details:\n\n"
            f"📖 Title: {json_youtube_details['title']}\n"
            f"📝 Description: {json_youtube_details['description']}\n"
            f"🔖 Tags: {json_youtube_details['tags']}\n"
            f"📅 Upload Date: {youtube_details['upload_date']}\n\n"
            f"🔗 URL: {youtube_details['url']}\n\n"
        )

    # Build TikTok section
    tiktok_section = ""
    if tiktok_details:
        tiktok_section = (
            f"\n\n🕺 TikTok Video Details:\n\n"
            f"📖 Title: {json_tiktok_details['title']}\n"
            f"📝 Description: {json_tiktok_details['description']}\n"
            f"🔖 Tags: {json_tiktok_details['tags']}\n"
            f"📅 Upload Date: {tiktok_details['upload_date']}\n\n"
            f"🔗 URL: {tiktok_details['url']}\n\n"
        )

    # Construct the message
    message = f"{heading}\n{title}\n{subreddit}\n{duration}\n{generated_data}{youtube_section}{tiktok_section}"

    return message


def send_telegram_message(data):
  
    message = create_message(data)
    send(message)
    
    


def send(message):
    config_data = config.load_configuration()
    try:
        api_url = f'https://api.telegram.org/bot{config_data["TELEGRAM_BOT_TOKEN"]}/sendMessage'
        params = {
            'chat_id': config_data["TELEGRAM_CHANNEL_ID"],
            'text': message
        }

        response = requests.post(api_url, params=params)

        if response.status_code != 200:
            logger.error(f"Error sending Telegram notification. Status code: {response.status_code}")
        logger.info("Message sent successfully!")
    except Exception as e:
        logger.error(f"Error sending message: {e}")