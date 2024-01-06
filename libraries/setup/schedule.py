from datetime import datetime, timedelta
import random
import json
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from fastapi import HTTPException
import os
from pathlib import Path
from utils.logger import setup_logger, get_logger
from app.libraries.video import generate_short_video
import pytz

setup_logger()
logger = get_logger()

FILE_PATH = "storage/scheduled_videos.json"
    

scheduler = BackgroundScheduler()
    
async def schedule_video_generation(dateandtime):
    global scheduler
    for item in dateandtime:
        schedule_time = datetime.fromisoformat(item)
        try:
            scheduler.add_job(generate_short_video, 'date', run_date=schedule_time, timezone=timezone('Asia/Colombo'))
            logger.info(f"Video scheduled for {schedule_time}")
        except Exception as e:
            logger.error(f"Error scheduling video for {schedule_time}: {e}")
            raise HTTPException(status_code=500, detail="Error scheduling video")
 
def generate_timestamp_sri_lanka():
    # Set timezone to Sri Lanka Standard Time
    sri_lanka_tz = pytz.timezone('Asia/Colombo')
    current_datetime = datetime.now(sri_lanka_tz)
    
    num_times = 4
    future_times = []
    
    # Calculate the end of the day in Sri Lankan time
    end_of_day = current_datetime.replace(hour=23, minute=30, second=00, microsecond=999999)
    remaining_seconds_today = (end_of_day - current_datetime).total_seconds()

    # Divide the remaining time into equal intervals
    interval = remaining_seconds_today / num_times

    for i in range(num_times):
        # Generate timestamps at each interval
        future_time = current_datetime + timedelta(seconds=interval * (i+1))
        future_times.append(future_time.strftime('%Y-%m-%d %H:%M:%S'))

    return future_times
                
                
async def start_scheduled_videos():
    global scheduler
    if scheduler.running:
        await stop_scheduled_videos()
        
    times = generate_timestamp_sri_lanka()
    if not scheduler.running:
        scheduler.start()
        await schedule_video_generation(times)
            
    return await view_scheduled_videos()

    
async def stop_scheduled_videos():
    global scheduler
    if scheduler.running:
        existing_data = await view_scheduled_videos()
        if existing_data:
            try:
                jobs = scheduler.get_jobs()
                for job in jobs:
                    job.remove()
                scheduler.shutdown()
                
                return True
            except Exception as e:
                logger.error(f"Error stopping scheduled videos: {e}")
                raise HTTPException(status_code=500, detail="Error stopping scheduled videos")
    else:
        logger.error(f"Error stopping scheduled videos: Scheduler not running")
        raise HTTPException(status_code=500, detail="Error stopping scheduled videos: Scheduler not running")
        

async def view_scheduled_videos():
    global scheduler
    
    jobs = scheduler.get_jobs()
    jobs_info = []
    for job in jobs:
        jobs_info.append({
            "id": job.id,
            "next_run_time": str(job.next_run_time),
            "name": job.name
        })
    return jobs_info