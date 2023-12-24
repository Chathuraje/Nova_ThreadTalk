from datetime import datetime
import pytz

def get_current_sri_lankan_time():
    utc_time = datetime.utcnow()
    sri_lankan_timezone = pytz.timezone('Asia/Colombo')
    sri_lankan_time = utc_time.replace(tzinfo=pytz.utc).astimezone(sri_lankan_timezone)

    return sri_lankan_time.timestamp()

def format_sri_lankan_time(timestamp):
    sri_lankan_timezone = pytz.timezone('Asia/Colombo')
    sri_lankan_time = datetime.fromtimestamp(timestamp, sri_lankan_timezone)
    
    # Format the time as a string
    formatted_time = sri_lankan_time.strftime('%Y-%m-%d %H:%M:%S %Z')
    
    return formatted_time

def get_time_after_15_minutes():
    current_time = get_current_sri_lankan_time()
    time_after_15_minutes = current_time + (15 * 60)  # 15 minutes in seconds

    sri_lankan_timezone = pytz.timezone('Asia/Colombo')
    time_after_15_minutes_datetime = datetime.fromtimestamp(time_after_15_minutes, sri_lankan_timezone)
    
    return time_after_15_minutes_datetime.isoformat()


def get_time_after_15_minutes_in_timestamp():
    time_after_15_minutes_isoformat = get_time_after_15_minutes()
    time_after_15_minutes_timestamp = datetime.fromisoformat(time_after_15_minutes_isoformat).timestamp()
    
    return time_after_15_minutes_timestamp
    