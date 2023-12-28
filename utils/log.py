from fastapi import HTTPException
from utils.response import StandardResponse, LogContent
from collections import deque
import traceback
from utils.logger import setup_logger, get_logger

setup_logger()
logger = get_logger()

def read_log(limit) ->  StandardResponse[LogContent]:
    try:
        with open("nova_threadtalk.log", "r") as log_file:
            if limit is None or limit < 0:
                log_content = [line.strip() for line in log_file]
            else:
                log_content = deque(log_file, maxlen=limit)
                log_content = list(log_content)
                
        return LogContent(logs=log_content)

    except FileNotFoundError as e:
        logger.error(f"Log file not found: {e}")
        raise HTTPException(status_code=404, detail="Log file not found") from e
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Error while reading log file: {e}\nTraceback: {tb}")
        raise HTTPException(status_code=500, detail=f"Error while reading log file: {e}\nTraceback: {tb}") from e