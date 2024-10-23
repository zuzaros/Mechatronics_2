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
import cv2.aruco as aruco

def automaticMissionControl():
    print("Running automatic mission control...")
    print("Starting mission in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("Automatic mission started!")

    # Create the grid map
    map_grid, pixels_per_cm_x, pixels_per_cm_y, min_x, min_y, grid_size_width, grid_size_height = create_grid_map()

    # Check if the grid map was created successfully
    if map_grid is None or map_grid.size == 0:
        print("Error: Failed to create the grid map.")
        return

    print(map_grid)
    time.sleep(1)

    # expand highground area
    expansion_size = 1
    rows, cols = len(map_grid), len(map_grid[0])
    grid = np.array(map_grid)  # Create a copy of the grid to avoid modifying the original

    # Identify highground cells
    highground_cells = [(i, j) for i in range(rows) for j in range(cols) if grid[i][j] == 1]

    # Expand highground area
    for i, j in highground_cells:
        for di in range(-expansion_size, expansion_size + 1):
            for dj in range(-expansion_size, expansion_size + 1):
                ni, nj = i + di, j + dj
                if 0 <= ni < rows and 0 <= nj < cols:
                    grid[ni][nj] = 1
    print ("Highground area expanded successfully!")
    print (grid)

 

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

                print("Ball detected at pixel position:", cX, cY)
                
                # Translate ball's pixel coordinates (cX, cY) into real-world coordinates (in cm)
                ball_x_cm = (cX-min_x)/pixels_per_cm_x
                ball_y_cm = (cY-min_y)/pixels_per_cm_y

                # Convert real-world coordinates to grid cell indices
                grid_x = int((ball_x_cm) / grid_size_width)
                grid_y = int((ball_y_cm) / grid_size_height)


                # Update the current position of the ball
                current_pos = [grid_x, grid_y]

                print("Ball detected at position:", current_pos)
            else:
                ball_detected = False
        else:
            print("Ball not detected - please put it in frame!")
            time.sleep(10)
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

    # #find best order to hit spice_targets
    # start = current_pos
    # spice_targets = FindTargets(grid, 2)
    # HG_targets = FindTargets(grid, 1)

    # permutations = []
    # length = [[] for _ in range(len(spice_targets) * (len(spice_targets) - 1) * (len(spice_targets) - 2))]
    # total_length = []
    # # Initialize event_grid
    # event_grid = np.zeros((len(map_grid), len(map_grid[0])))

    # # Generate permutations of spice targets
    # for i in range(len(spice_targets)):
    #     for j in range(len(spice_targets)):
    #         if j != i:
    #             for k in range(len(spice_targets)):
    #                 if k != i and k != j:
    #                     permutations.append((start, spice_targets[i], spice_targets[j], spice_targets[k], start))

    # # Calculate path lengths for each permutation
    # for a in range(len(permutations)):
    #     for b in range(len(permutations[a]) - 1):
    #         length[a].append(len(A_Star(permutations[a][b], permutations[a][b + 1], map_grid)))
    #     total_length.append(sum(length[a]))

    # # Choose the permutation with the shortest total length
    # chosen_permutation = permutations[total_length.index(min(total_length))]

    # print(chosen_permutation)

    # # Find and store path for all spice_targets combined
    # path = []

    # for i in range(len(chosen_permutation) - 1):
    #     path.append(A_Star(chosen_permutation[i], chosen_permutation[i + 1], grid))

    # for i in range(len(path)):
    #     j = 1

    # # Initialize the camera feed and other variables
    # camera_feed = cv2.VideoCapture(0)  # Change 0 to the path of your video file if needed
    # i = 0
    # j = 0
    # worm_trigger = 0 #default
    # worm_trigger_counter = 0 #default
    # last_checked_time = 0  # Initialize last check time
    # check_interval = 5  # 3 seconds between checks

    # if not camera_feed.isOpened():
    #     print("Failed to open camera or video file.")
    #     return

    # # Read the first frame to get the dimensions
    # ret, frame = camera_feed.read()
    # if not ret:
    #     print("Failed to read from camera or video file.")
    #     return
    
    # # Convert the frame to grayscale for ArUco detection
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # # Detect markers and their poses using the existing detectMarkers function
    # corners, ids, tvecs = detectMarkers(gray)

    # #reset variables
    # current_target = path[i][j+1]

    # while i <= len(path):
    #     while j < len(path[i]):
    #         executing_value = int(MQTTread("Executing"))
    #         if executing_value == 0:    
    #             while True:
    #                 current_time = time.time()

    #                 # Capture the current frame from the camera feed
    #                 ret, frame = camera_feed.read()

    #                 if not ret:
    #                     print("Failed to capture frame.")
    #                     break

    #                 # Convert the frame to grayscale for ArUco detection
    #                 gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #                 # Detect markers and their poses using the existing detectMarkers function
    #                 corners, ids, tvecs = detectMarkers(gray)

    #                 # Display the frame with detected markers and IDs
    #                 if ids is not None:
    #                     aruco.drawDetectedMarkers(frame, corners, ids)
    #                 cv2.imshow('Mission Control Feed', frame)

    #                 # Perform checks and operations only if the interval has passed
    #                 if current_time - last_checked_time >= check_interval:
    #                     last_checked_time = current_time  # Update last check time

    #                 # Track BabySpice’s position (marker 4)
    #                 if ids is not None and 4 in ids.flatten():
    #                     marker_index = np.where(ids == 4)[0][0]
    #                     marker_corners = corners[marker_index]

    #                     # Calculate the center of the detected marker
    #                     marker_center = np.mean(marker_corners[0], axis=0)
    #                     marker_x, marker_y = int(marker_center[0]), int(marker_center[1])

    #                     # Convert pixel position to grid coordinates
    #                     grid_x = int((marker_x - min_x) / (pixels_per_cm_x * 5))  # grid_size is 5 cm
    #                     grid_y = int((marker_y - min_y) / (pixels_per_cm_y * 5))

    #                     # Update the current position of the robot
    #                     current_pos = [grid_x, grid_y]

    #                     # Calculate the orientation of the marker
    #                     # The orientation can be determined by the angle of the line connecting two corners
    #                     corner_0 = marker_corners[0][0]  # First corner
    #                     corner_1 = marker_corners[0][1]  # Second corner
    #                     dx = corner_1[0] - corner_0[0]
    #                     dy = corner_1[1] - corner_0[1]
    #                     angle = np.degrees(np.arctan2(dy, dx))
    #                     # current orientation of the robot
    #                     # round the angle to the nearest multiple of 90 degrees 
    #                     current_dir = round(angle / 90) * 90
    #                     # if output is 360, set it to 0
    #                     if current_dir == 360:
    #                         current_dir = 0
                        
    #                 else:
    #                     print("BabySpice not detected - please put her in frame!")

    #                     # Check if the sandworm (marker 5) is in frame
    #                     sandworm_present = False
    #                     if ids is not None:
    #                         sandworm_present = 5 in ids.flatten()  # Check for sandworm marker

    #                     if sandworm_present:
    #                         worm_trigger = 1
    #                         print ("Worm detected, redirecting to high ground")
    #                     else:
    #                         worm_trigger = 0

    #                 # if q is pressed, exit the loop
    #                 if cv2.waitKey(1) & 0xFF == ord('q'):
    #                     break

    #             #check if the target has been reached
    #             # current position can be within 1 cell of the target
    #             # this is to account for any errors in the robot's movement
    #             if current_pos[0] in range(current_target[0]-1, current_target[0]+2) and current_pos[1] in range(current_target[1]-1, current_target[1]+2):

    #                 #check if worm trigger is on
    #                 if worm_trigger == 1:
    #                     worm_trigger_counter += 1

    #                     #check if it is the first time the worm trigger has been on
    #                     if  worm_trigger_counter == 1:
                            
    #                         #find closest high ground
    #                         distance_to_HG = []
    #                         for k in range(len(HG_targets)):
    #                             distance_to_HG.append(len(A_Star(current_pos, HG_targets[k], event_grid)))
    #                         chosen_HG = HG_targets[distance_to_HG.index(min(distance_to_HG))]
    #                         #find path to HG and back to position before worm trigger
    #                         event_path = A_Star(current_pos, chosen_HG, event_grid)
    #                         a = 1
    #                         while a < len(event_path)-1:
    #                             if direction(path[a-1], path[a]) == direction(path[a], path[a+1]):
    #                                 event_path[a].remove(path[i][j])
    #                             else:
    #                                 a += 1
    #                         reverse_event_path = event_path.reverse() #need to check that this does what you want it to do
    #                         event_path.append(reverse_event_path)
    #                         event_path.remove(event_path[0])
    #                         #add to main path list
    #                         path[i][j+1:j+1] = event_path

    #                 #move on to next point and reset worm trigger counter
    #                 worm_trigger_counter = 0
    #                 j += 1

    #             #if the target has not been reached
    #             else:
    #                 MOTOR_DIRECTIONS, RPM, TIME = CreateRobotCommands(current_pos, current_dir, current_target)
    #                 MQTTwrite("M1_Dir", MOTOR_DIRECTIONS[0])
    #                 MQTTwrite("M2_Dir", MOTOR_DIRECTIONS[1])
    #                 MQTTwrite("M1_RPM", RPM)
    #                 MQTTwrite("M2_RPM", RPM)
    #                 MQTTwrite("TIME", TIME)
    #         else:
    #             print("Waiting for robot to finish executing order")

    #     print("Target reached, Collecting spice")
    #     #move on to next target set
    #     i += 1
    #     j = 0

    #     # if q is pressed, exit the loop
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break
                    
        
    # print("All spice collected and returned to start")


    # Release camera feed and close all OpenCV windows
    camera_feed.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    automaticMissionControl()