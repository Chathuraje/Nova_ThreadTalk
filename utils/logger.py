import logging
from colorlog import ColoredFormatter
from fastapi import HTTPException
from config import config

log_setup_done = False  # Flag to track whether logging setup is already done

class ExcludeHttpRequestFilter(logging.Filter):
    def filter(self, record):
        # Exclude log messages related to the HTTP request
        http_request_message = "HTTP Request: POST https://api.openai.com/v1/chat/completions"
        
        # Constant substring in the YouTube API-related log message
        # youtube_api_constant_substring = 'HTTP/1.1'
        # google_drive_string = 'oauth2client<4.0.0'

        return http_request_message not in record.getMessage()
    
# class CustomStreamHandler(logging.StreamHandler):
#     def emit(self, record):
#         if record.levelno == logging.ERROR:
            
#             raise HTTPException(status_code=404, detail=record.getMessage()) 
#         super().emit(record)    

def setup_logger():
    global log_setup_done
    STAGE  = config.get_mode()
    
    if not log_setup_done:
        if STAGE == "DEVELOPMENT":
            FORMAT_LOG = '%(bold_red)s{}%(reset)s %(log_color)s%(levelname)-8s%(reset)s %(green)s%(asctime)s - %(white)s%(message)s'.format("DEV")
            FORMAT_SAVE = f'DEV %(levelname)-8s %(asctime)s - %(message)s'
        elif STAGE == "PRODUCTION":
            FORMAT_LOG = '%(reset)s %(log_color)s%(levelname)-8s%(reset)s %(green)s%(asctime)s - %(white)s%(message)s'
            FORMAT_SAVE = f'%(levelname)-8s %(asctime)s - %(message)s'
        
        formatter = ColoredFormatter(
            FORMAT_LOG,
            datefmt="%Y-%m-%d %H:%M:%S",
            reset=True,
            log_colors={
                'DEBUG': 'bold_cyan',
                'INFO': 'bold_green',
                'WARNING': 'bold_yellow',
                'ERROR': 'bold_red',
                'CRITICAL': 'bold_red,bg_white',
            }
        )

        logging.basicConfig(filename='nova_threadtalk.log', level=logging.INFO, format=FORMAT_SAVE)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        console_handler.addFilter(ExcludeHttpRequestFilter())
        
        # error_handler = CustomStreamHandler()
        # error_handler.setLevel(logging.ERROR)
        # error_handler.setFormatter(formatter)
        
        logging.getLogger().addHandler(console_handler)
        # logging.getLogger().addHandler(error_handler)

        log_setup_done = True

def get_logger():
    return logging.getLogger()