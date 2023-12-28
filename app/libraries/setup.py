from utils.logger import setup_logger, get_logger
from libraries.setup import setup
from libraries.setup import schedule
from libraries.video_generator import telegram
import datetime
import pytz
from libraries.setup import db

setup_logger()
logger = get_logger()


def upload_json_secrets(file):
    logger.info(f'Starting upload...')
    setup.upload_json_secrets(file)
    logger.info(f'Upload completed successfully!')

def initial_setup():
    logger.info(f'Starting setup...')
        
    logger.info(f'Setting up database...')
    db.setup_db()
    logger.info(f'Setup database successfully!')
    
    logger.info('Start downloading background videos...')
    setup.download_background_videos()
    logger.info('Background videos downloaded successfully!')
    
    logger.info('Checking video resolution...')
    setup.check_video_resolution()
    logger.info('Video resolution checked successfully!')
    
    logger.info('Generating Scheduled Timestamps...')
    schedule.stop_scheduled_videos()
    timestamps = schedule.generate_timestamp()
    schedule.start_scheduled_videos()
    logger.info('Scheduled Timestamps generated successfully!')
    
    logger.info('Setup completed successfully!')
    
    
    sorted_timestamps = sorted(timestamps, key=lambda x: x['timestamp'])

    message = "Video Generation Schedule:\n"
    for item in sorted_timestamps:
        timestamp = datetime.datetime.fromisoformat(item['timestamp'])
        formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')
        message += f"- {formatted_time}\n"
        
    message += f"Setup completed successfully! Video scheduled successfully!"
    telegram.send(message)
    
    