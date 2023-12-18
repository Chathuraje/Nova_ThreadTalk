import logging
from colorlog import ColoredFormatter

log_setup_done = False  # Flag to track whether logging setup is already done

def setup_logger():
    global log_setup_done

    if not log_setup_done:
        formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )

        logging.basicConfig(filename='nova_redditautogen.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)

        log_setup_done = True

def get_logger():
    return logging.getLogger()
