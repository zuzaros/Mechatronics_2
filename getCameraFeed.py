# getCameraFeed.py

import cv2

def getCameraFeed():
    # Select the first camera (0) that is connected to the machine
    cap = cv2.VideoCapture(0)
    # Set the width and height of the camera to 640x480
    cap.set(3, 640)
    cap.set(4, 480)
    return cap
