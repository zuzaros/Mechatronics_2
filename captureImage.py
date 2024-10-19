from getCameraFeed import getCameraFeed
import cv2
import numpy as np

def captureImage():
    # Load camera calibration results
    calibration_data = np.load('sample_calibration.npz')

    # Debugging: Print the keys in the calibration file
    print("Keys in the calibration file:", calibration_data.files)

    # Access the camera matrix and distortion coefficients using the correct keys
    camera_matrix = calibration_data['CM']
    dist_coeffs = calibration_data['dist_coef']
    
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

        # Undistort and sharpen the captured frame
        sharpening_kernel = np.array([[-1, -1, -1, -1, -1],
                                    [-1,  2,  2,  2, -1],
                                    [-1,  2,  8,  2, -1],
                                    [-1,  2,  2,  2, -1],
                                    [-1, -1, -1, -1, -1]]) / 8.0
                                    
        sharpened_frame = cv2.filter2D(frame, -1, sharpening_kernel)

        undistorted_frame = cv2.undistort(sharpened_frame, camera_matrix, dist_coeffs)

        # Display the resulting frame
        cv2.imshow('Live Feed', undistorted_frame)
        
        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

    return undistorted_frame

# Run the captureImage function
if __name__ == "__main__": 
    captureImage()
