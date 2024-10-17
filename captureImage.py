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

    # Display the camera feed in a loop
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

    return frame

# Run the captureImage function
if __name__ == "__main__":
    captureImage()
