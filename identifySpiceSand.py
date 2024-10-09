import cv2
import numpy as np

def identifySpiceSand(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Detect "spice" areas (light-colored)
    light_lower = np.array([0, 0, 200], dtype=np.uint8)
    light_upper = np.array([180, 50, 255], dtype=np.uint8)
    spice_mask = cv2.inRange(hsv, light_lower, light_upper)

    # Detect "sand" areas (dark-colored)
    dark_lower = np.array([0, 0, 0], dtype=np.uint8)
    dark_upper = np.array([180, 255, 50], dtype=np.uint8)
    sand_mask = cv2.inRange(hsv, dark_lower, dark_upper)

    spice = cv2.findNonZero(spice_mask)
    sand = cv2.findNonZero(sand_mask)
    
    return spice, sand
