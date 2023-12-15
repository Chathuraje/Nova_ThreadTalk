import os
import configparser

# Access config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

VIDEO_LENGTH = config.get('Settings', 'VIDEO_LENGTH')
MIN_COMMENT_WORDS = int(config.get('Settings', 'MIN_COMMENT_WORDS'))
MAX_COMMENT_WORDS = int(config.get('Settings', 'MAX_COMMENT_WORDS'))
SCREENSHOT_WIDTH = int(config.get('Settings', 'SCREENSHOT_WIDTH'))
SCREENSHOT_HEIGHT = int(config.get('Settings', 'SCREENSHOT_HEIGHT'))