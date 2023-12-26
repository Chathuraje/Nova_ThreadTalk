from datetime import datetime, timedelta
import random
import json
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from utils.log import setup_logger, get_logger

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
    
def schedule_video_generation(scheduler, dateandtime):
    for item in dateandtime:
        schedule_time = datetime.fromisoformat(item["timestamp"])
        scheduler.add_job(generate_video, 'date', run_date=schedule_time, timezone=timezone('Asia/Colombo'))         

def schedule_videos(date, num_times):
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
        return {"message": "Video scheduling complete.", "data": dateandtime}
    except Exception as e:
        logger.error(f"Error during scheduling videos: {e}")
      
def start_scheduled_videos():
    try:
        with open("storage/scheduled_videos.json") as file:
            data = json.load(file)
            scheduler = BackgroundScheduler()
            scheduler.start()
            schedule_video_generation(scheduler, data)
            return {"message": "Scheduled videos started."}
    except Exception as e:
        logger.error(f"Error starting scheduled videos: {e}")  
        
def stop_scheduled_videos():
    try:
        write_to_json_file([])
        return {"message": "Scheduled videos stopped."}
    except Exception as e:
        logger.error(f"Error stopping scheduled videos: {e}")
        

def view_scheduled_videos():
    try:
        with open("storage/scheduled_videos.json") as file:
            data = json.load(file)
            return {"message": "Scheduled videos fetched.", "data": data}
    except Exception as e:
        logger.error(f"Error viewing scheduled videos: {e}")