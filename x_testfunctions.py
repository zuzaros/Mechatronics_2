import cv2
import time
from x_mainLoop import process_frame

# Read the JPG image
image_path = 'sample.jpg'
frame = cv2.imread(image_path)

ret = True  # Typically True if the frame is successfully read

# Call the function with the ret value and the frame
overlay_frame, highground, spice, sand, babySpice, sandworm = process_frame(ret, frame)

# show the overlay_frame to visualize the result
cv2.imshow("Live Feed with Overlay", overlay_frame)
cv2.waitKey(0)
cv2.destroyAllWindows
