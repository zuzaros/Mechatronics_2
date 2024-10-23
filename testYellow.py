import numpy as np
import cv2
import time
from makeGridMap import create_grid_map
from FindTargets import FindTargets
from A_Star import A_Star, direction
from CreateRobotCommands import CreateRobotCommands
from MQTTread import MQTTread
from MQTTwrite import MQTTwrite
from detectMarkers import detectMarkers

def automaticMissionControl():
    print("Running automatic mission control...")
    print("Starting mission in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("Automatic mission started!")

    # # Create the grid map
    # map_grid, pixels_per_cm_x, pixels_per_cm_y, min_x, min_y = create_grid_map()

    # # Check if the grid map was created successfully
    # if map_grid is None or map_grid.size == 0:
    #     print("Error: Failed to create the grid map.")
    #     return

    # print(map_grid)

    # grid = map_grid

    # Initialize the camera feed
    camera_feed = cv2.VideoCapture(0)  # Change 0 to the path of your video file if needed

    if not camera_feed.isOpened():
        print("Failed to open camera or video file.")
        return

    ball_detected = False

    while not ball_detected:
        ret, frame = camera_feed.read()
        if not ret:
            print("Failed to capture frame.")
            break

        # Convert the frame to HSV for color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define the color range for the ball (e.g., yellow)
        lower_color = np.array([20, 100, 100])
        upper_color = np.array([30, 255, 255])

        # Create a mask for the color
        mask = cv2.inRange(hsv, lower_color, upper_color)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Check if any contours are found
        if contours:
            # Find the largest contour
            largest_contour = max(contours, key=cv2.contourArea)

            # Calculate the center of the largest contour
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                ball_detected = True

                # Draw the contour and center of the ball on the frame
                cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)
                cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)
                cv2.putText(frame, "Ball", (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                # # Convert pixel position to grid coordinates
                # grid_x = int((cX - min_x) / (pixels_per_cm_x * 5))  # grid_size is 5 cm
                # grid_y = int((cY - min_y) / (pixels_per_cm_y * 5))

                # # Update the current position of the ball
                # current_pos = [grid_x, grid_y]

                # print("Ball detected at position:", current_pos)
            else:
                ball_detected = False
        else:
            print("Ball not detected - please put it in frame!")
            ball_detected = False

        # Display the frame
        cv2.imshow('Mission Control Feed', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    time.sleep(5)

    print("Calculating the path of BabySpice to collect all the spice and return to the starting point.")

    # Release camera feed and close all OpenCV windows
    camera_feed.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    automaticMissionControl()