import cv2
import os
import time
import threading
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
import configparser

# --- CONFIGURATION ---

# Read initial config values from a config file (config.ini)
# Example config.ini content:
# [DEFAULT]
# fps = 18
# clip_duration = 10
# source_folder = ./clips
# webcam_ip = http://172.16.16.78:5001/video
# use_fixed_video = False
# fixed_video_path = 

config = configparser.ConfigParser()
config.read("config.ini")
DEFAULT = config["DEFAULT"]

fps = int(DEFAULT.get("fps", 60))
clip_duration = int(DEFAULT.get("clip_duration", 120))  # seconds
source_folder = DEFAULT.get("source_folder", "./clips")
webcam_ip = DEFAULT.get("webcam_ip", "http://172.16.16.78:5001/video")
use_fixed_video = DEFAULT.getboolean("use_fixed_video", False)
fixed_video_path = DEFAULT.get("fixed_video_path", "")

if not os.path.exists(source_folder):
    os.makedirs(source_folder)

class VideoProcessor:
    def __init__(self):
        self.running = False
        self.thread = None
        self.cap = None
        self.clip_counter = 1
        self.use_fixed_video = use_fixed_video
        self.fps = fps
        self.clip_duration = clip_duration
        self.source_folder = source_folder
        self.webcam_ip = webcam_ip
        self.fixed_video_path = fixed_video_path

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.process_video, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()
        if self.cap is not None:
            self.cap.release()

    def process_video(self):
        source = self.fixed_video_path if self.use_fixed_video and self.fixed_video_path else self.webcam_ip
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            print(f"Error opening video source: {source}")
            self.running = False
            return

        time.sleep(1.0)  # allow camera to warm up
        prev_frame = None
        recording = False
        clip_writer = None
        clip_start_time = None

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame, ending capture.")
                break

            # Convert to grayscale and blur for simple motion detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            if prev_frame is None:
                prev_frame = gray
                continue

            # Compute difference between frames
            frame_delta = cv2.absdiff(prev_frame, gray)
            thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            motion_score = cv2.countNonZero(thresh)

            # If motion score exceeds threshold, start (or continue) recording
            if motion_score > 5000:
                if not recording:
                    clip_filename = os.path.join(self.source_folder, f"{self.clip_counter}.mp4")
                    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                    height, width = frame.shape[:2]
                    clip_writer = cv2.VideoWriter(clip_filename, fourcc, self.fps, (width, height))
                    recording = True
                    clip_start_time = time.time()
                    print(f"Motion detected. Starting clip: {clip_filename}")
                else:
                    clip_writer.write(frame)

                if time.time() - clip_start_time >= self.clip_duration:
                    clip_writer.release()
                    self.clip_counter += 1
                    recording = False
                    clip_writer = None
                    clip_start_time = None
                    print("Clip ended due to duration limit.")
            else:
                # If no significant motion but still recording, keep writing until clip duration is met
                if recording:
                    clip_writer.write(frame)
                    if time.time() - clip_start_time >= self.clip_duration:
                        clip_writer.release()
                        self.clip_counter += 1
                        recording = False
                        clip_writer = None
                        clip_start_time = None
                        print("Clip ended (no further motion).")

            prev_frame = gray
            time.sleep(0.05)

        if self.cap:
            self.cap.release()


app = FastAPI()
processor = VideoProcessor()

@app.post("/start")
def start_processing():
    """
    Starts the background video processing.
    """
    if not processor.running:
        processor.start()
    return {"status": "processing started"}

@app.post("/stop")
def stop_processing():
    """
    Stops the background video processing.
    """
    if processor.running:
        processor.stop()
    return {"status": "processing stopped"}

# Data model for toggling video input source.
class InputSwitch(BaseModel):
    use_fixed_video: bool
    fixed_video_path: str = None

@app.post("/switch_input")
def switch_input(input_data: InputSwitch):
    """
    Switches the input source.
    If use_fixed_video is True, the processor will use the provided fixed_video_path.
    """
    processor.use_fixed_video = input_data.use_fixed_video
    if input_data.use_fixed_video and input_data.fixed_video_path:
        processor.fixed_video_path = input_data.fixed_video_path
    return {
        "status": "input switched",
        "use_fixed_video": processor.use_fixed_video,
        "fixed_video_path": processor.fixed_video_path
    }

# Data model for updating configuration parameters.
class UpdateConfig(BaseModel):
    fps: int = None
    clip_duration: int = None
    source_folder: str = None

@app.post("/update_config")
def update_config(cfg: UpdateConfig):
    """
    Updates configuration parameters. These parameters will affect how future clips are recorded.
    """
    if cfg.fps is not None:
        processor.fps = cfg.fps
    if cfg.clip_duration is not None:
        processor.clip_duration = cfg.clip_duration
    if cfg.source_folder is not None:
        processor.source_folder = cfg.source_folder
        if not os.path.exists(processor.source_folder):
            os.makedirs(processor.source_folder)
    return {
        "status": "config updated",
        "fps": processor.fps,
        "clip_duration": processor.clip_duration,
        "source_folder": processor.source_folder
    }

@app.get("/status")
def status():
    """
    Returns the current processing status.
    """
    return {
        "running": processor.running,
        "use_fixed_video": processor.use_fixed_video,
        "clip_counter": processor.clip_counter
    }
