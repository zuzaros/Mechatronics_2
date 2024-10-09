# Calculate the distance between acuro markers shown via a camera

# This is the vision library OpenCV
import cv2
# This is a library for mathematical functions for python (used later)
import numpy as np
# This is a library to get access to time-related functionalities
import time
import cv2.aruco as aruco


# Select the first camera (0) that is connected to the machine
# in Laptops should be the build-in camera
cap = cv2.VideoCapture(0)

# Set the width and heigth of the camera to 640x480
cap.set(3,640)
cap.set(4,480)

# Create a named win
cv2.namedWindow("frame-image", cv2.WINDOW_AUTOSIZE)

# Load the camera calibration values
Camera=np.load('Sample_Calibration.npz')
CM=Camera['CM'] #camera matrix
dist_coef=Camera['dist_coef']# distortion coefficients from the camera

# Create an aruco dictiona
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()
marker_tvecs = []  # Initialize marker_tvecs as an empty list


# Execute this continuously

while(True):

    # Start the performance clock
    start = time.perf_counter()


    # Capture current frame from the camera
    ret, frame = cap.read()

    if not ret:
        print("Failed to capture image")
        continue
    

    # Convert the image from the camera to Gray scale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    corners, ids, rP = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    out = aruco.drawDetectedMarkers(frame, corners, ids) #This overlays the markers

    rvecs,tvecs,_objPoints = aruco.estimatePoseSingleMarkers(corners,100,CM,dist_coef)

    if ids is not None:
        for ind, id in enumerate(ids):
            out = cv2.drawFrameAxes(out, CM, dist_coef,rvecs[ind], tvecs[ind], 30)
    time.sleep(0.2)

    # Display the original frame in a window
    cv2.imshow("frame-image", out)

    # Calculate the distance between the markers
    if ids is not None:
        # Create a dictionary to store the translation vectors of the markers
        marker_tvecs = {id[0]: tvecs[ind] for ind, id in enumerate(ids)}

    # Check if both marker 0 and marker 2 are detected
    if 0 in marker_tvecs and 2 in marker_tvecs:
        # Calculate the Euclidean distance between marker 0 and marker 2
        distance = np.linalg.norm(marker_tvecs[0] - marker_tvecs[2])
        print("Distance between marker 0 and marker 2: ", distance)


    # If the key 'q' is pressed, break from the loop
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break
    
