import cv2
import requests
import numpy as np
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "dummy_key")

def send_chunk_to_openai(frames):
    _, buffer = cv2.imencode('.jpg', frames[0])
    image_bytes = buffer.tobytes()

    # Example of a "mock" request
    # response = requests.post(
    #     "https://api.openai.com/v1/video-analyze",  # Example endpoint
    #     headers={
    #         "Authorization": f"Bearer {OPENAI_API_KEY}",
    #         "Content-Type": "application/octet-stream",
    #     },
    #     data=image_bytes
    # )
    #
    # result = response.json()

    # Mock result
    result = {
        "status": "success",
        "description": "Detected motion in video chunk. Potentially a person walking."
    }

    return result
