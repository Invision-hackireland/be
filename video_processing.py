import cv2
import time
import numpy as np

def capture_and_detect_motion(camera_ip, chunk_duration=30, wait_duration=5, min_motion_frames=5):
    """
    Capture video from `camera_ip`, detect motion, and yield 30-second chunks (list of frames).
    If there is no motion in the entire chunk, skip sending it.

    :param camera_ip: IP or URL to the camera feed (e.g. rtsp:// or http://).
    :param chunk_duration: Duration (in seconds) for which frames are buffered.
    :param wait_duration: Pause (in seconds) after each chunk is processed.
    :param min_motion_frames: Minimum number of frames that contain motion
                              within the chunk to be considered "active."
    """
    cap = cv2.VideoCapture(camera_ip)
    if not cap.isOpened():
        print(f"Error: Unable to open camera stream at {camera_ip}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:  
        # Fallback if FPS is not detected. Provide a safe default.
        fps = 20.0

    # Simple background frame for naive motion detection
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read first frame from camera.")
        cap.release()
        return

    prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_buffer = []
    motion_count = 0

    chunk_start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # End of stream or error

        current_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Simple frame differencing approach
        diff = cv2.absdiff(prev_gray, current_gray)
        # Threshold the difference to obtain regions of motion
        _, diff_thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        # Count the number of non-zero pixels => measure motion
        non_zero_count = np.count_nonzero(diff_thresh)

        # Heuristic: if non_zero_count is above some threshold, declare motion
        # The threshold below is arbitrary and depends on actual scene
        motion_detected = non_zero_count > 10000

        if motion_detected:
            motion_count += 1

        # Store the frame in our buffer
        frame_buffer.append(frame)
        prev_gray = current_gray

        # Check if chunk_duration (30 seconds) has passed
        elapsed = time.time() - chunk_start_time
        if elapsed >= chunk_duration:
            # If we had enough motion in this chunk, yield it
            if motion_count >= min_motion_frames:
                yield frame_buffer

            # Reset for the next chunk
            frame_buffer = []
            motion_count = 0
            chunk_start_time = time.time()

            # Wait the specified duration before capturing the next chunk
            time.sleep(wait_duration)

    cap.release()
