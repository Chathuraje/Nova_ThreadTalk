from utils.logger import setup_logger, get_logger
from libraries.setup import schedule
from utils.response import ViewScheduledVideoResponse, ViewScheduledVideo, StopScheduledVideoRespose
from libraries.video_generator import telegram

setup_logger()
logger = get_logger()


async def start_scheduled_videos() -> ViewScheduledVideoResponse:
    timestamps = await schedule.start_scheduled_videos()
    
    message = "Video Generation Schedule:\n"
    for item in timestamps:
        message += f"- {item['next_run_time']}\n"
        
    message += f"Video scheduled successfully!"
    telegram.send(message)
    
    video_data = [ViewScheduledVideo(**item) for item in timestamps]
    return ViewScheduledVideoResponse(code=200, data=video_data)

async def stop_scheduled_videos() -> StopScheduledVideoRespose:
    await schedule.stop_scheduled_videos()
    return StopScheduledVideoRespose(code=200, data={'status': 'stopped'})
    
async def view_scheduled_videos() -> ViewScheduledVideoResponse:
    data = await schedule.view_scheduled_videos()
    video_data = [ViewScheduledVideo(**item) for item in data]
    
    return ViewScheduledVideoResponse(code=200, data=video_data)