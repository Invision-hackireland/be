from fastapi import FastAPI
from pydantic import BaseModel  # Import BaseModel from pydantic
from video_processor import VideoProcessor
import os
from fastapi.middleware.cors import CORSMiddleware

from routers import room_router, camera_router, user_router, rule_router, logs_router, dashboard_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

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

class InputSwitch(BaseModel):
    use_fixed_video: bool
    fixed_video_path: str = None

@app.post("/switch_input")
def switch_input(input_data: InputSwitch):
    """
    Maintenance API: Switches video input source.
    """
    processor.use_fixed_video = input_data.use_fixed_video
    if input_data.use_fixed_video and input_data.fixed_video_path:
        processor.fixed_video_path = input_data.fixed_video_path
    return {
        "status": "input switched",
        "use_fixed_video": processor.use_fixed_video,
        "fixed_video_path": processor.fixed_video_path
    }

class UpdateConfig(BaseModel):
    fps: int = None
    clip_duration: int = None
    source_folder: str = None

@app.post("/update_config")
def update_config(cfg: UpdateConfig):
    """
    Updates configuration parameters for video processing.
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
app.include_router(room_router)
app.include_router(camera_router)
app.include_router(user_router)
app.include_router(rule_router)
app.include_router(logs_router)
app.include_router(dashboard_router)
