from datetime import datetime, timedelta
import random
import json
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from utils.log import setup_logger, get_logger
from fastapi import HTTPException
import os

setup_logger()
logger = get_logger()

def generate_random_times(date_str, num_times):
     # Convert string to datetime
    given_date = datetime.strptime(date_str, '%Y-%m-%d')

    # If the given date is today, start from the current time, else start from midnight
    start_time = datetime.now() if given_date.date() == datetime.today().date() else datetime(given_date.year, given_date.month, given_date.day)

    times = []
    for _ in range(num_times):
        # Generate a random time during the day, after the start_time
        intervals_from_start = (start_time.hour * 60 + start_time.minute) // 15
        total_intervals = 96  # Total 15-minute intervals in a day
        random_interval = random.randint(intervals_from_start, total_intervals - 1)
        random_time = datetime(given_date.year, given_date.month, given_date.day) + timedelta(minutes=random_interval * 15)
        times.append(random_time.strftime("%Y-%m-%d %H:%M:%S"))

    return times

def write_to_json_file(data):
    FILE_PATH = "storage/scheduled_videos.json"
    
    try:
        with open(FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)
    except IOError as e:
        print(f"An error occurred while writing to JSON file: {e}") 
            
def generate_video():
    print("Generating video..asdasd.")
    


scheduler = BackgroundScheduler()
    
def schedule_video_generation(scheduler, dateandtime):
    for item in dateandtime:
        schedule_time = datetime.fromisoformat(item["timestamp"])
        scheduler.add_job(generate_video, 'date', run_date=schedule_time, timezone=timezone('Asia/Colombo'))
        logger.info(f"Video scheduled for {schedule_time}")      

def generate_timestamp():
    date = datetime.now().strftime('%Y-%m-%d')
    num_times = 4
    
    try:
        times = generate_random_times(date, num_times)
        dateandtime = []
        for time in times:
            dateandtime.append({
                "timestamp": f"{time}+05:30",
                # "human_readable_time": f"{time} +0530",
                # "selected": False
            })
        write_to_json_file(dateandtime)
        return dateandtime
    except Exception as e:
        logger.error(f"Error during scheduling videos")
      

def check_timestamp_latest():
    with open("storage/scheduled_videos.json") as file:
        data = json.load(file)

        now_utc = datetime.now(timezone('UTC'))
        for item in data:
            timestamp_str = item['timestamp']
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S%z")

            if timestamp < now_utc:
                logger.error(f"Timestamp {timestamp_str} is in the past.")
                
                
def start_scheduled_videos():
    existing_data = view_scheduled_videos()
    if existing_data:
            logger.error("Scheduled videos already started.")
    else:
        check_timestamp_latest()
        if not scheduler.running:
            scheduler.start()
            
        FILE_PATH = "storage/scheduled_videos.json"
        if not os.path.exists(FILE_PATH):
            return {"message": "No videos scheduled."}
        
        with open() as file:
            data = json.load(file)
            schedule_video_generation(scheduler, data)
            return view_scheduled_videos()

    
        
        
def stop_scheduled_videos():
    if scheduler.running:
        existing_data = view_scheduled_videos()
        if existing_data:
            try:
                jobs = scheduler.get_jobs()
                
                for job in jobs:
                    job.remove()
                scheduler.shutdown()
                return {"message": "Scheduled videos stopped."}
            except Exception as e:
                logger.error(f"Error stopping scheduled videos: {e}")
        
        else:
            return {"message": "No videos scheduled."}
    else:
        logger.error(f"Scheduled videos already stopped.")
        

def view_scheduled_videos():
    jobs = scheduler.get_jobs()
    jobs_info = []
    for job in jobs:
        jobs_info.append({
            "id": job.id,
            "next_run_time": str(job.next_run_time),
            "name": job.name
        })
    return jobs_info