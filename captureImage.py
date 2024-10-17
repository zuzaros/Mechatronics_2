from getCameraFeed import getCameraFeed
import cv2

def captureImage():
    # initialize the camera feed
    cap = getCameraFeed()

    # Check if cap is None
    if cap is None:
        print("No camera or video feed available.")
        return None

    # create window
    cv2.namedWindow("Live Feed", cv2.WINDOW_NORMAL)

    # Check if the camera feed is available
    if cap is None or not cap.isOpened():
        print("Failed to open camera")
        return None
 
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Check if frame is captured successfully
        if not ret:
            print("Failed to capture frame or end of video reached.")
            break

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
