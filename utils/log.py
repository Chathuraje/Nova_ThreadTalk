from fastapi import HTTPException
from utils.response import StandardResponse, LogContent
from collections import deque
import traceback


def read_log(limit) ->  StandardResponse[LogContent]:
    try:
        with open("nova_threadtalk.log", "r") as log_file:
            if limit is None or limit < 0:
                log_content = [line.strip() for line in log_file]
            else:
                log_content = deque(log_file, maxlen=limit)
                log_content = list(log_content)
                
        return LogContent(logs=[log_content])

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Log file not found") from e
    except Exception as e:
        tb = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Error while reading log file: {e}\nTraceback: {tb}") from e