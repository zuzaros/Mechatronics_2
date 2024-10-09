# mainLoop.py

# import the necessary libraries
import cv2
import numpy as np
import time
import cv2.aruco as aruco

# Import functions
from getCameraFeed import getCameraFeed
from detectMarkers import detectMarkers
from identifyHighground import identifyHighground
from identifySpiceSand import identifySpiceSand
from objectTracking import objectTracking
from createMap import createMap
from overlayMap import overlayMap

def process_frame(ret, frame):
    if not ret:
        return None

    # Detect markers in the frame
    corners, ids = detectMarkers(frame)

    # Identify highground, spice, and sand areas
    highground = identifyHighground(ids, corners)
    spice, sand = identifySpiceSand(frame)

    # Track babySpice (marker0) and sandworm (marker1)
    babySpice = objectTracking(ids, corners, 0)  # Tracking babySpice
    sandworm = objectTracking(ids, corners, 1)   # Tracking sandworm

    # Create map of environment and overlay live feed
    createMap(highground, spice, sand, babySpice, sandworm)

    map_data = {
        'babySpice': [babySpice],
        'sandworm': [sandworm]
    }
    overlay_frame = overlayMap(frame, map_data)

    return overlay_frame, highground, spice, sand, babySpice, sandworm

def mainLoop():

    # initialize the camera feed
    cap = getCameraFeed()

    if cap is None or not cap.isOpened():
        print("Failed to open camera")
        return
    
    # Execute this continuously
    while(True):
        ret, frame = cap.read()  # Capture current frame from the camera
        result = process_frame(ret, frame)
        
        if result:
            overlay_frame, highground, spice, sand, babySpice, sandworm = result
            cv2.imshow("Live Feed with Overlay", overlay_frame)
        else:
            break

        # exit the loop if 'q' key is pressed
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

# run the main loop
mainLoop()