import os
import shutil
from utils.log import setup_logger, get_logger

setup_logger()
logger = get_logger()


def read_all_videos():
    storage_folder = "storage/"
    all_videos = []
    
    for folder_name in os.listdir(storage_folder):
        folder_path = os.path.join(storage_folder, folder_name)

        if os.path.isdir(folder_path):
            video_name = folder_name
            all_videos.append({"name": video_name})

    return all_videos


def delete_video_folder(video_id):
    storage_folder = "storage/"
    folder_path = os.path.join(storage_folder, video_id)
 
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        return {"message": "Video deleted successfully!"}
        
    else:
        logger.info("The file does not exist")
        return {"message": "The file does not exist"}
    