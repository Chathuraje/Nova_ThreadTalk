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