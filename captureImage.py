# this function captures the camera feed, processes the frame and detect markers
# it then creates a grid map of highground, spice and sand

#import the necessary libraries
import cv2
import time

# Import functions
from getCameraFeed import getCameraFeed

def captureImage():
    # initialize the camera feed
    cap = getCameraFeed()

    # create window
    cv2.namedWindow("Live Feed", cv2.WINDOW_NORMAL)

    # Check if the camera feed is available
    if cap is None or not cap.isOpened():
        print("Failed to open camera")
        return None
 
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Display the resulting frame
        cv2.imshow('Live Feed', frame)
        
        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

    # Return the last processed frame
    return frame

# run
if __name__ == "__main__":
    # This code will only run if this file is executed directly
    captureImage()
