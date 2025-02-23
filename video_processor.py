import cv2
import os
import time
import threading
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load configurations from .env
FPS = int(os.getenv("FPS", 30))
CLIP_DURATION = int(os.getenv("CLIP_DURATION", 120))
SOURCE_FOLDER = os.getenv("SOURCE_FOLDER", "./clips")
TMP_FOLDER = os.getenv("TMP_FOLDER", "./tmp")
WEBCAM_IP = os.getenv("WEBCAM_IP", "http://192.168.236.101:5000/video_feed")
USE_FIXED_VIDEO = os.getenv("USE_FIXED_VIDEO", "False").lower() == "true"
FIXED_VIDEO_PATH = os.getenv("FIXED_VIDEO_PATH", "")

# Ensure source folder exists
os.makedirs(SOURCE_FOLDER, exist_ok=True)
os.makedirs(TMP_FOLDER, exist_ok=True)

class VideoProcessor:
    def __init__(self):
        self.running = False
        self.thread = None
        self.cap = None
        self.clip_counter = 1
        self.use_fixed_video = USE_FIXED_VIDEO
        self.fps = FPS
        self.clip_duration = CLIP_DURATION
        self.source_folder = SOURCE_FOLDER
        self.webcam_ip = WEBCAM_IP
        self.fixed_video_path = FIXED_VIDEO_PATH

    def start(self):
        """Starts the video processing thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.process_video, daemon=True)
            self.thread.start()
            logging.info("Video processing started.")

    def stop(self):
        """Stops video processing and cleans up resources."""
        self.running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()
        logging.info("Video processing stopped.")

    def process_video(self):
        """Handles video capture, motion detection, and recording."""
        source = self.fixed_video_path if self.use_fixed_video and self.fixed_video_path else self.webcam_ip
        self.cap = cv2.VideoCapture(source)

        if not self.cap.isOpened():
            logging.error(f"Error opening video source: {source}")
            self.running = False
            return

        prev_frame = None
        recording = False
        clip_writer = None
        clip_start_time = None

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                logging.warning("Failed to grab frame, ending capture.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            if prev_frame is None:
                prev_frame = gray
                continue

            # Motion detection logic
            frame_delta = cv2.absdiff(prev_frame, gray)
            thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            motion_score = cv2.countNonZero(thresh)

            # Start recording if motion detected
            if motion_score > 5000:
                if not recording:
                    clip_filename = os.path.join(self.source_folder, f"{self.clip_counter}.mp4")
                    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                    height, width = frame.shape[:2]
                    clip_writer = cv2.VideoWriter(clip_filename, fourcc, self.fps, (width, height))
                    recording = True
                    clip_start_time = time.time()
                    logging.info(f"Motion detected. Starting clip: {clip_filename}")

                clip_writer.write(frame)

                # Stop recording after clip duration
                if time.time() - clip_start_time >= self.clip_duration:
                    clip_writer.release()
                    self.clip_counter += 1
                    recording = False
                    clip_writer = None
                    clip_start_time = None
                    logging.info("Clip ended due to duration limit.")

            elif recording:
                clip_writer.write(frame)
                if time.time() - clip_start_time >= self.clip_duration:
                    clip_writer.release()
                    self.clip_counter += 1
                    recording = False
                    clip_writer = None
                    clip_start_time = None
                    logging.info("Clip ended (no further motion).")

            prev_frame = gray
            time.sleep(0.05)

        if self.cap:
            self.cap.release()
