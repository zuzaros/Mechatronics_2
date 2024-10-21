# getCameraFeed.py

import cv2
import os

def getCameraFeed():
    # Select the first camera (0) that is connected to the machine
    cap = cv2.VideoCapture(0)
    # Set the width and height of the camera to 640x480
    cap.set(3, 640)
    cap.set(4, 480)
    
    # Check if the camera feed is available
    if not cap.isOpened():
        print("Failed to open camera, attempting to use video file instead.")
        video_path = os.path.join('videos', 'driveTest_1.mp4')
        print(f"Trying to open video file at: {video_path}")
        
        # Check if the file exists
        if not os.path.exists(video_path):
            print(f"Video file does not exist at: {video_path}")
            return None
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Failed to open video file")
            return None
    
    print("Camera or video feed opened successfully.")
    return cap
