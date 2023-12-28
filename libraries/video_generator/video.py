import multiprocessing
import ffmpeg
import tempfile
import threading
import time
import math
from utils.logger import setup_logger, get_logger
from tqdm import tqdm
import os
import random
from utils.data import read_json, check_ongoing, update_json, create_json
from utils.time import get_current_sri_lankan_time

setup_logger()
logger = get_logger()

VIDEO_WIDTH = 2160
class ProgressFfmpeg(threading.Thread):
    def __init__(self, vid_duration_seconds, progress_update_callback):
        threading.Thread.__init__(self, name="ProgressFfmpeg")
        self.stop_event = threading.Event()
        self.output_file = tempfile.NamedTemporaryFile(mode="w+", delete=False)
        self.vid_duration_seconds = vid_duration_seconds
        self.progress_update_callback = progress_update_callback

    def run(self):
        while not self.stop_event.is_set():
            latest_progress = self.get_latest_ms_progress()
            if latest_progress is not None:
                completed_percent = latest_progress / self.vid_duration_seconds
                self.progress_update_callback(completed_percent)
            time.sleep(1)

    def get_latest_ms_progress(self):
        lines = self.output_file.readlines()

        if lines:
            for line in lines:
                if "out_time_ms" in line:
                    out_time_ms_str = line.split("=")[1].strip()
                    if out_time_ms_str.isnumeric():
                        return float(out_time_ms_str) / 1000000.0
                    else:
                        # Handle the case when "N/A" is encountered
                        return None
        return None

    def stop(self):
        self.stop_event.set()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args, **kwargs):
        self.stop()

def __check_if_video_exists(reddit_id, reddit):
    video_path = f"storage/{reddit_id}/{reddit_id}.mp4"
    if os.path.exists(video_path):
        durations = reddit['duration']
        if durations == 0:
            return False
        return True
    else:
        return False

def make_final_video():
    VIDEO_LENGTH = 60
    reddit_id = check_ongoing()
    reddit = read_json(reddit_id)
    
    if __check_if_video_exists(reddit_id, reddit):
        logger.info(f"Post {reddit_id} already has video. Skipping...")
        return None
    
    logger.info(f"Making video for: {reddit['title']}")
        
    logger.info(f"Gathering Background Video")
    background_video_path = f"data/background_videos/"
    all_files = os.listdir(background_video_path)
    video_files = [file for file in all_files if file.endswith(('.mp4', '.avi', '.mkv', '.mov'))]
        
    if not video_files:
        logger.error("No video files found in the folder.")
        exit()
    else:
        random_video = random.choice(video_files)
        selected_video_path = os.path.join(background_video_path, random_video)
            
        background_clip = ffmpeg.input(selected_video_path)
        background_clip_duration = float(ffmpeg.probe(selected_video_path)["format"]["duration"])

        
    logger.info(f"Gathering Audio Clips")
        
    clip_directory = f"storage/{reddit_id}/voice/"
    files = os.listdir(clip_directory)
    number_of_clips = len(files)
        
    try:
        audio_clips = []
        audio_clips_durations = []

        # Add title clip first
        title_clip_path = f"storage/{reddit_id}/voice/title.mp3"
        title_duration = float(ffmpeg.probe(title_clip_path)["format"]["duration"])
        if title_duration <= VIDEO_LENGTH:
            audio_clips.append(ffmpeg.input(title_clip_path))
            audio_clips_durations.append(title_duration)

        for i in range(1, number_of_clips):
            clip_path = f"storage/{reddit_id}/voice/{i}.mp3"
            duration = float(ffmpeg.probe(clip_path)["format"]["duration"])

            if sum(audio_clips_durations) + duration <= VIDEO_LENGTH:
                audio_clips.append(ffmpeg.input(clip_path))
                audio_clips_durations.append(duration)
            else:
                break  # Stop adding clips if the total duration exceeds VIDEO_LENGTH

    except ffmpeg.Error as e:
        logger.error(f"ffprobe error: {e.stderr.decode()}")

        
        
    audio_concat = ffmpeg.concat(*audio_clips, a=1, v=0)
    ffmpeg.output(
        audio_concat, f"storage/{reddit_id}/audio.mp3", **{"b:a": "192k"}
    ).overwrite_output().run(quiet=True)
    final_audio = ffmpeg.input(f"storage/{reddit_id}/audio.mp3")


    logger.info("Gathering Image Clips")
    screenshot_width = int((VIDEO_WIDTH * 94) // 100)

    image_clips = list()
    image_clips.insert(
        0,
        ffmpeg.input(f"storage/{reddit_id}/image/title.png")["v"].filter(
            "scale", screenshot_width, -1
        ),
    )

    current_time = 0
    total_overlay_duration = math.ceil(sum(audio_clips_durations))
    logger.info(f"Video Will Be: {total_overlay_duration} Seconds Long")
        
    if background_clip_duration < total_overlay_duration:
        repetitions = int(total_overlay_duration / background_clip_duration)
        remaining_duration = total_overlay_duration % background_clip_duration
        background_clips = [background_clip] * repetitions

        if remaining_duration > 0:
            partial_clip = background_clip.filter('trim', duration=remaining_duration)
            background_clips.append(partial_clip)
            
        background_clip = ffmpeg.concat(*background_clips, v=1, a=0)
    elif background_clip_duration > total_overlay_duration:
        background_clip = background_clip.filter('trim', duration=total_overlay_duration)

    for i in range(0, number_of_clips):
        image_clips.append(
            ffmpeg.input(f"storage/{reddit_id}/image/{i+1}.png")["v"].filter(
                "scale", screenshot_width, -1
            )
        )
        image_overlay = image_clips[i].filter("colorchannelmixer")
        background_clip = background_clip.overlay(
            image_overlay,
            enable=f"between(t,{current_time},{current_time + audio_clips_durations[i]})",
            x="(main_w-overlay_w)/2",
            y="(main_h-overlay_h)/2",
        )
        current_time += audio_clips_durations[i]



    logger.info("Rendering the video....")
        
    pbar = tqdm(total=100, desc="Progress: ", bar_format="{l_bar}{bar}", unit=" %")

    def on_update_example(progress) -> None:
        status = round(progress * 100, 2)
        old_percentage = pbar.n
        pbar.update(status - old_percentage)

    defaultPath = f"storage/{reddit_id}"
        
    with ProgressFfmpeg(total_overlay_duration, on_update_example) as progress:
        path = defaultPath + f"/{reddit_id}"
        path = (
            path[:251] + ".mp4"
        )  # Prevent a error by limiting the path length, do not change this.
        try:
            ffmpeg.output(
                background_clip,
                final_audio,
                path,
                f="mp4",
                **{
                    "c:v": "h264",
                    "b:v": "20M",
                    "b:a": "192k",
                    "threads": multiprocessing.cpu_count(),
                },
            ).overwrite_output().global_args("-progress", progress.output_file.name).run(
                quiet=True,
                overwrite_output=True,
                capture_stdout=False,
                capture_stderr=False,
            )
        except ffmpeg.Error as e:
            logger.error(e.stderr.decode("utf8"))
            exit(1)
    old_percentage = pbar.n
    pbar.update(100 - old_percentage)
    pbar.close()
    logger.info(f"Video creation complete for video: {reddit['title']} and saved to: {path}")
    
    reddit['generated_date'] = get_current_sri_lankan_time()
    reddit['duration'] = total_overlay_duration
    
    update_json(reddit)