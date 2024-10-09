# This is the vision library OpenCV
import cv2
# This is a library for mathematical functions for python (used later)
import numpy as np
# This is a library to get access to time-related functionalities
import time


# Select the first camera (0) that is connected to the machine
# in Laptops should be the build-in camera
cap = cv2.VideoCapture(0)

# Set the width and heigth of the camera to 640x480
cap.set(3,640)
cap.set(4,480)

#Create four opencv named windows
cv2.namedWindow("frame-image", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("gray-image", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("binary-image", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("edges-image", cv2.WINDOW_AUTOSIZE)

#Position the windows next to eachother
cv2.moveWindow("frame-image", 0, 0)         # Top-left corner
cv2.moveWindow("gray-image", 640, 0)        # Top-right corner
cv2.moveWindow("binary-image", 0, 360)      # Bottom-left corner
cv2.moveWindow("edges-image", 640, 360)     # Bottom-right corner


# Execute this continuously
while(True):
    
    # Start the performance clock
    start = time.perf_counter()
    
    # Capture current frame from the camera
    ret, frame = cap.read()
    
    # Convert the image from the camera to Gray scale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Implement canny edge detection
    edges = cv2.Canny(gray,100,200)
    
    # Display the original frame in a window
    cv2.imshow('frame-image',frame)

    # Display the grey image in another window
    cv2.imshow('gray-image',gray)

    # Display the edges in another window
    cv2.imshow('edges-image',edges)
    
    # convert the gray image to a binary image
    # the threshold value is 100
    ret,thresh = cv2.threshold(gray,100,255,cv2.THRESH_BINARY)

    # Display the binary image in another window
    cv2.imshow('binary-image',thresh)
    
    # Stop the performance counter
    end = time.perf_counter()
    
    # Print to console the exucution time in FPS (frames per second)
    print ('{:4.1f}'.format(1/(end - start)))

    # If the button q is pressed in one of the windows 
    if cv2.waitKey(20) & 0xFF == ord('q'):
        # Exit the While loop
        break
    

# When everything done, release the capture
cap.release()
# close all windows
cv2.destroyAllWindows()
# exit the kernel
exit(0)