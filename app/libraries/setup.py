from utils.logger import setup_logger, get_logger
from libraries.setup import setup
from libraries.setup import schedule
from libraries.video_generator import telegram
import datetime
import pytz
from libraries.setup import db
from utils.response import UploadJsonFileResponse, InitialSetupResponse, ViewScheduledVideo
from apscheduler.schedulers.background import BackgroundScheduler
from utils import scheduler

setup_logger()
logger = get_logger()


async def upload_json(file) -> UploadJsonFileResponse:
    data = await setup.upload_json(file)
    
    return UploadJsonFileResponse(code=200, data=data)

async def initial_setup() -> InitialSetupResponse:    
    db_setup = False
    db_connect = await db.setup_db()
    if db_connect is not None:
        db_setup = True
    
    video_list = await setup.download_background_videos()
    await setup.check_video_resolution()
    
    timestamps = await schedule.start_scheduled_videos()
    
    message = "Video Generation Schedule:\n"
    for item in timestamps:
        message += f"- {item['next_run_time']}\n"
    message += f"Video scheduled successfully!"
    telegram.send(message)
    
    video_data = [ViewScheduledVideo(**item) for item in timestamps]
    
    data = {
        'status': 'success',
        'db_setup': db_setup,
        'video_downloaded': video_list,
        'scheduled_at': video_data
    }
    
    return InitialSetupResponse(code=200, data=data)
    
    