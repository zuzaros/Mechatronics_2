# this file is the main file for the automatic mission control
"""
automaticMissionControl.py
This file is the main file for the automatic mission control. It is responsible for running the automatic mission control system.
Functions:
    automaticMissionControl(): Executes the automatic mission control sequence, 
    including creating a grid map, monitoring for sandworm presence, and managing the mission's progress.
Usage:
    This script should be executed directly to run the automatic mission control.
"""
# it will be responsible for the following:
# running the automatic mission control

# import the necessary libraries
import time
import cv2
import numpy as np
import cv2.aruco as aruco

# import the necessary functions
from makeGridMap import create_grid_map
from A_Star import A_Star, direction
from CreateRobotCommands_V2 import CreateRobotCommands
from MQTTread import MQTTread
from MQTTwrite_V2 import MQTTwrite 
from detectMarkers import detectMarkers
from FindTargets import FindTargets

def semiAutomaticMissionControl():
    print("Running automatic mission control...")
    print("Starting mission in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("Automatic is starting started!")

    # Create the grid map
    map_grid, pixels_per_cm_x, pixels_per_cm_y, min_x, min_y, grid_size_width, grid_size_height = create_grid_map()

    # check if the grid map was created successfully
    if map_grid is None:
        print("Failed to create the grid map.")
        return
    
    print ("Grid map created successfully!")
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

    babyspice_detected = False
    correct_orientation = False
    current_pos = [3, 3]  # Set starting position to (0, 0)

    while not babyspice_detected or not correct_orientation:
        ret, frame = camera_feed.read()
        if not ret:
            print("Failed to capture frame.")
            break

        # Convert the frame to grayscale for ArUco detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect markers and their poses using the existing detectMarkers function
        corners, ids, tvecs = detectMarkers(gray)

        # Display the frame with detected markers and IDs
        if ids is not None:
            aruco.drawDetectedMarkers(frame, corners, ids)
        cv2.imshow('Mission Control Feed', frame)

        # BabySpice detection logic
        if ids is not None and 4 in ids.flatten():
            marker_index = np.where(ids == 4)[0][0]
            marker_corners = corners[marker_index]

            # ask user to confirm if BabySpice is in the correct position
            user_input = input("Is BabySpice in the correct position? (y/n): ")
            if user_input.lower() == 'y':
                babyspice_detected = True

            # Calculate the orientation of the marker
            corner_0 = marker_corners[0][0]  # First corner
            corner_1 = marker_corners[0][1]  # Second corner
            dx = corner_1[0] - corner_0[0]
            dy = corner_1[1] - corner_0[1]
            angle = np.degrees(np.arctan2(dy, dx))
            current_dir = round(angle / 5) * 5

            # Check if orientation is correct
            if current_dir != 0:
                print("Error: BabySpice is not facing the correct direction.")
                correct_orientation = False
            else:
                print("BabySpice is ready to start the mission!")
                print("Starting position:", current_pos)
                correct_orientation = True

        else:
            print("BabySpice not detected - please put her in frame!")
            babyspice_detected = False
            correct_orientation = False

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

    # find best order to hit spice_targets
    start = current_pos
    spice_targets = FindTargets(grid, 2)
    HG_targets = FindTargets(grid, 1)
    permutations = []
    length = [[] for _ in range(len(spice_targets) * (len(spice_targets) - 1) * (len(spice_targets) - 2))]
    total_length = []

    # Initialize event_grid
    event_grid = np.zeros((len(map_grid), len(map_grid[0])))

    # Generate permutations of spice targets
    for i in range(len(spice_targets)):
        for j in range(len(spice_targets)):
            if j != i:
                for k in range(len(spice_targets)):
                    if k != i and k != j:
                        permutations.append((start, spice_targets[i], spice_targets[j], spice_targets[k], start))

    # Calculate path lengths for each permutation
    for a in range(len(permutations)):
        for b in range(len(permutations[a]) - 1):
            length[a].append(len(A_Star(permutations[a][b], permutations[a][b + 1], map_grid)))
        total_length.append(sum(length[a]))

    # Choose the permutation with the shortest total length
    chosen_permutation = permutations[total_length.index(min(total_length))]

    print(chosen_permutation)

    # Find and store path for all spice_targets combined
    path = []

    for i in range(len(chosen_permutation) - 1):
        path.append(A_Star(chosen_permutation[i], chosen_permutation[i + 1], grid))

      #only keep important points (start, spice_targets and turning points)
    for i in range(len(path)):
        j = 1
        while j < len(path[i])-1:
            if direction(path[i][j-1], path[i][j]) == direction(path[i][j], path[i][j+1]):
                path[i].remove(path[i][j])
            else:
                j += 1

    print(path)  

    ########## Connect to MQTT
    import paho.mqtt.client as mqtt

    def on_connect(client,userdata,flags,rc):
        print ("Connected to MQTT")
        client.subscribe("babyspice/Executing")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg):
        received_messages.append(int(msg.payload.decode()))

    client = mqtt.Client()
    received_messages = []
    client.on_connect = on_connect
    client.on_message = on_message

    client.username_pw_set("student","HousekeepingGlintsStreetwise")
    client.connect("fesv-mqtt.bath.ac.uk",31415,60)

    client.loop_start()

    # Initialize the camera feed and other variables
    camera_feed = cv2.VideoCapture(0)  # Change 0 to the path of your video file if needed
    i = 0
    j = 0
    worm_trigger = 0  # default
    worm_trigger_counter = 0  # default
    last_checked_time = 0  # Initialize last check time
    check_interval = 5  # 3 seconds between checks

    if not camera_feed.isOpened():
        print("Failed to open camera or video file.")
        return

    # Read the first frame to get the dimensions
    ret, frame = camera_feed.read()
    if not ret:
        print("Failed to read from camera or video file.")
        return
    
    # Convert the frame to grayscale for ArUco detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect markers and their poses using the existing detectMarkers function
    corners, ids, tvecs = detectMarkers(gray)

    # reset variables
    current_target = path[i][j + 1]

    while i <= len(path):
        while j < len(path[i]):
            executing_value = int(MQTTread("Executing"))
            if executing_value == 0:    
                while True:
                    current_time = time.time()

                    # Capture the current frame from the camera feed
                    ret, frame = camera_feed.read()

                    if not ret:
                        print("Failed to capture frame.")
                        break

                    # Convert the frame to grayscale for ArUco detection
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    # Detect markers and their poses using the existing detectMarkers function
                    corners, ids, tvecs = detectMarkers(gray)

                    # Display the frame with detected markers and IDs
                    if ids is not None:
                        aruco.drawDetectedMarkers(frame, corners, ids)
                    cv2.imshow('Mission Control Feed', frame)

                    # Perform checks and operations only if the interval has passed
                    if current_time - last_checked_time >= check_interval:
                        last_checked_time = current_time  # Update last check time

                    # Check if any sandworms are detected
                    if (time.time() - last_checked_time) >= check_interval:
                        last_checked_time = time.time()
                        if ids is not None and 2 in ids.flatten():
                            worm_trigger = 1
                            worm_trigger_counter = 0
                        else:
                            worm_trigger = 0

                        # Handle sandworm presence logic
                       #check if worm trigger is on
                    if worm_trigger == 1:
                        worm_trigger_counter += 1

                        #check if it is the first time the worm trigger has been on
                        if  worm_trigger_counter == 1:

                            #ask user to input the current position of the robot
                            current_pos = input("Please input the current position of the robot: ")
                            current_pos = current_pos.split(",")
                            current_pos = [int(current_pos[0]), int(current_pos[1])]


                            #find closest high ground
                            distance_to_HG = []
                            for k in range(len(HG_targets)):
                                distance_to_HG.append(len(A_Star(current_pos, HG_targets[k], event_grid)))
                            chosen_HG = HG_targets[distance_to_HG.index(min(distance_to_HG))]
                            #find path to HG and back to position before worm trigger
                            event_path = A_Star(current_pos, chosen_HG, event_grid)
                            a = 1
                            while a < len(event_path)-1:
                                if direction(path[a-1], path[a]) == direction(path[a], path[a+1]):
                                    event_path[a].remove(path[i][j])
                                else:
                                    a += 1
                            reverse_event_path = event_path.reverse() #need to check that this does what you want it to do
                            event_path.append(reverse_event_path)
                            event_path.remove(event_path[0])
                            #add to main path list
                            path[i][j+1:j+1] = event_path

                    #move on to next point and reset worm trigger counter
                    worm_trigger_counter = 0
                    j += 1

            #if the target has not been reached
            else:
                #ask user to input the current position of the robot
                current_pos = input("Please input the current position of the robot: ")
                current_pos = current_pos.split(",")
                current_pos = [int(current_pos[0]), int(current_pos[1])]

                MOTOR_DIRECTIONS, RPM, TIME = CreateRobotCommands(current_pos, current_dir, current_target)

                Time_Units = int(TIME)
                Time_Decimals = int(round((TIME - Time_Units) * 100))
                
                MQTTwrite("M1_Dir", MOTOR_DIRECTIONS[0])
                MQTTwrite("M2_Dir", MOTOR_DIRECTIONS[1])
                MQTTwrite("M1_RPM", RPM)
                MQTTwrite("M2_RPM", RPM)
                MQTTwrite("Time_Units", Time_Units)
                MQTTwrite("Time_Decimals", Time_Decimals)
                
                #give robot time to update executing value
                time.sleep(5)

        else:
            print("Waiting for robot to finish executing order")
            time.sleep(5)

        print("Target reached, Collecting spice")
            
        #action to be performed when collecting spice
        time.sleep(10)

        #move on to next target set
        i += 1
        j = 0
                

    print("All spice collected and returned to start")
                  

    # Release camera feed and close all OpenCV windows
    camera_feed.release()
    cv2.destroyAllWindows()

# Ensure the script runs the automatic mission control when executed
if __name__ == "__main__":
    semiAutomaticMissionControl()
