import asyncio
import telegram
from config.config import TELEGRAM_CHANNEL_ID, TELEGRAM_BOT_TOKEN
from utils.log import setup_logger, get_logger
from telegram.constants import ParseMode
from telegram.ext import Updater, CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime

setup_logger()
logger = get_logger()

def initialize_bot():
    try:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        logger.info("Telegram bot initialized successfully!")
        return bot
    except Exception as e:
        logger.error(f"Error initializing telegram bot: {e}")
        return None

def create_message(reddit_details):
    keyboard = []
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    headding = f"<b>📰 Generated YouTune Short Details:</b> {current_time}\n"
    
    title = f"<b>🔍 {reddit_details['title']} </b>\n"
    
    subreddit = f"<b>🌐 Subreddit:</b> r/{reddit_details['subreddit']}"
    duration = f"<b>⏳ Duration:</b> {reddit_details['duration']} seconds"
    generated_data = f"<b>📅 Generated Data:</b> {reddit_details['generated_data']}"

    youtube_details = reddit_details.get('youtube_details')
    youtube_section = ""
    if youtube_details:
        youtube_section = (
            f"\n\n<b>🎬 YouTube Video Details:</b>\n\n"
            f"<b>📖 Title:</b> {youtube_details['title']}\n"
            f"<b>📝 Description:</b> {youtube_details['description']}\n"
            f"<b>🔖 Tags:</b> {youtube_details['tags']}\n"
            f"<b>📅 Upload Date:</b> {youtube_details['upload_date']}\n\n"
            f"<b>🔗 URL:</b> {youtube_details['url']}\n\n"
        )

    tiktok_details = reddit_details.get('tiktok_details')
    tiktok_section = ""
    if tiktok_details:
        tiktok_section = (
            f"\n\n<b>🕺 TikTok Video Details:</b>\n\n"
            f"<b>📖 Title:</b> {tiktok_details['title']}\n"
            f"<b>📝 Description:</b> {tiktok_details['description']}\n"
            f"<b>🔖 Tags:</b> {tiktok_details['tags']}\n"
            f"<b>📅 Upload Date:</b> {tiktok_details['upload_date']}\n\n"
            f"<b>🔗 URL:</b> {tiktok_details['url']}\n\n"
        )
        
    keyboard.append([InlineKeyboardButton("View Reddit", url=reddit_details['url'])])
        
    if youtube_details is not None:
        keyboard.append([InlineKeyboardButton("View YouTube", url=youtube_details['url'])])
    if tiktok_details is not None:
        keyboard.append([InlineKeyboardButton("View TikTok", url=tiktok_details['url'])])

    reply_markup = InlineKeyboardMarkup(keyboard)


    message = f"{headding}\n{title}\n{subreddit}\n{duration}\n{generated_data}{youtube_section}{tiktok_section}"
    return message, reply_markup


async def send_telegram_message(data):
    bot = initialize_bot()
    if not bot:
        return

    message, reply_markup = create_message(data)
    
    try:
        await bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        logger.info("Message sent successfully!")
    except Exception as e:
        logger.error(f"Error sending message: {e}")
