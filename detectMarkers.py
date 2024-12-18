import cv2
import cv2.aruco as aruco#
# This is a library for mathematical functions for python (used later)
import numpy as np

def detectMarkers(binary):

    Camera=np.load('Sample_Calibration.npz') #Load the camera calibration values
    CM=Camera['CM'] #camera matrix
    dist_coef=Camera['dist_coef']# distortion coefficients from the camera

    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    parameters = aruco.DetectorParameters()
    
    corners, ids, rP = aruco.detectMarkers(binary, aruco_dict, parameters=parameters)

    rvecs,tvecs,_objPoints = aruco.estimatePoseSingleMarkers(corners,100,CM,dist_coef)
    
    if ids is not None:
        for ind, id in enumerate(ids):
            out = cv2.drawFrameAxes(binary, CM, dist_coef,rvecs[ind], tvecs[ind], 30)
   
            
    return corners, ids, tvecs