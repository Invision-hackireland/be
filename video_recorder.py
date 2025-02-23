import cv2
import os
import time
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load configurations from .env
TMP_FOLDER = os.getenv("TMP_FOLDER", "./tmp")
WEBCAM_IP = os.getenv("WEBCAM_IP", "http://192.168.236.101:5000/video_feed")
DEFAULT_FPS = 30  # Set a standard FPS to avoid frame jitter

# Ensure tmp folder exists
os.makedirs(TMP_FOLDER, exist_ok=True)

class VideoSnippetRecorder:
    def __init__(self, duration=20):
        self.duration = duration
        self.webcam_ip = WEBCAM_IP
        self.tmp_folder = TMP_FOLDER

        print("now")
        """Records a 30-second video snippet from the webcam and returns the file path."""
        self.cap = cv2.VideoCapture(self.webcam_ip)
        

    def record_snippet(self):
        if not self.cap.isOpened():
            logging.error(f"Error opening video source: {self.webcam_ip}")
            self.cap = cv2.VideoCapture(self.webcam_ip)
        
        print("noww")

        # Generate file path
        timestamp = int(time.time())
        file_path = os.path.join(self.tmp_folder, f"snippet_{timestamp}.avi")
        
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.cap.get(cv2.CAP_PROP_FPS) or DEFAULT_FPS  # Fallback if FPS is 0
        
        if width == 0 or height == 0:
            logging.error("Invalid frame size from webcam.")
            self.cap.release()
            return None
        
        out = cv2.VideoWriter(file_path, fourcc, fps, (width, height))

        logging.info(f"Recording video snippet: {file_path} at {fps} FPS")
        frame_count = 0
        total_frames = int(fps * self.duration)

        while frame_count < total_frames:
            ret, frame = self.cap.read()
            if not ret:
                logging.warning("Failed to grab frame, stopping recording.")
                break
            
            out.write(frame)
            frame_count += 1  # Keep track of frames written
        
        out.release()
        logging.info(f"Recording complete: {file_path}")
        return file_path

# Usage example
if __name__ == "__main__":
    recorder = VideoSnippetRecorder()
    video_path = recorder.record_snippet()
    print(f"Video saved at: {video_path}")
    video_path = recorder.record_snippet()
    print(f"Video saved at: {video_path}")
