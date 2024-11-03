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
# running the automatic mission controlq

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
from MQTTwrite import MQTTwrite 
from detectMarkers import detectMarkers
from FindTargets import FindTargets

def babySpiceDetection(frame, corners, ids, min_x, min_y, pixels_per_cm_x, pixels_per_cm_y):
    # BabySpice detection logic
    if ids is not None and 4 in ids.flatten():
        marker_index = np.where(ids == 4)[0][0]
        marker_corners = corners[marker_index]
        # Calculate the orientation of the marker
        corner_0 = marker_corners[0][0]
        corner_1 = marker_corners[0][1]
        dx = corner_1[0] - corner_0[0]
        dy = corner_1[1] - corner_0[1]
        angle = np.degrees(np.arctan2(dy, dx))
        current_dir = round(angle / 10) * 10

        if current_dir < 0:
                current_dir += 360

        print("BabySpice orientation:", current_dir)

        # Calculate the center of the detected marker
        marker_center = np.mean(marker_corners[0], axis=0)
        marker_x, marker_y = int(marker_center[0]), int(marker_center[1])

        print(f"BabySpice's position: (X: {marker_x}, Y: {marker_y})")

        # Convert pixel position to grid coordinates
        grid_x = int((marker_x - min_x) / (pixels_per_cm_x * 5))  # grid_size is 5 cm
        grid_y = int((marker_y - min_y) / (pixels_per_cm_y * 5))

        print(f"BabySpice's grid position: (Row: {grid_y}, Col: {grid_x})")
        current_pos = (grid_y, grid_x)

    return current_pos, current_dir

def sandwormDetection(ids):
    # Check for the presence of the sandworm marker (ID 5)
    return ids is not None and 5 in ids.flatten()

def mostlyAutomaticMissionControl():
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

    # Initialize camera feed
    camera_feed = cv2.VideoCapture(0)  # Use 0 for live camera feed or change it to the video file path
    if not camera_feed.isOpened():
        print("Failed to open camera.")
        return

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

    # BabySpice detection loop
    babyspice_detected, correct_orientation = False, False
    while not babyspice_detected or not correct_orientation:
        ret, frame = camera_feed.read()
        if not ret:
            print("Failed to capture frame.")
            break
        
        # Detect markers
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = detectMarkers(gray)
        if ids is not None:
            aruco.drawDetectedMarkers(frame, corners, ids)
            cv2.imshow("Mission Control Feed", frame)

        current_pos, current_dir = babySpiceDetection(frame, corners, ids, min_x, min_y, pixels_per_cm_x, pixels_per_cm_y)

        if current_pos is not None:
            babyspice_detected = True
            if current_dir != 0:
                print("Error: BabySpice is not facing the correct direction.")
                correct_orientation = False
            else:
                print("BabySpice's orientation is:", current_dir)
                print("BabySpice is ready to start the mission!")
                print("Starting position:", current_pos)
                correct_orientation = True
        else:
            print("BabySpice not detected - please put her in frame!")
            babyspice_detected = False
            time.sleep(1)

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

    # Initialize variables
    i = 0
    j = 0
    worm_trigger = 0  # default
    worm_trigger_counter = 0  # default
    last_checked_time = 0  # Initialize last check time
    check_interval = 5  # 3 seconds between checks
    

    while i <= len(path)-1:
        while j < len(path[i])-1:
            time.sleep(2)
            #executing value is the last message received from the robot in background. When received_messages is empty, the executing value is 0 so it can enter the loop
            if len(received_messages) > 0:
                executing_value = received_messages[-1]
            else:
                executing_value = 0

            if executing_value == 0:  
                current_target = path[i][j+1]
                print("Current target:", current_target)
                          
                # Capture a new frame in each iteration to detect BabySpice's position
                ret, frame = camera_feed.read()
                if not ret:
                    print("Failed to capture frame.")
                    break

                # Convert frame to grayscale and detect markers
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                corners, ids, _ = detectMarkers(gray)  # Update corners and ids in each iteration

                if ids is not None:
                    # Optionally, draw detected markers for debugging purposes
                    aruco.drawDetectedMarkers(frame, corners, ids)
                    cv2.imshow("Mission Control Feed", frame)
                
                # Call BabySpice detection with updated frame and marker info
                current_pos, current_dir = babySpiceDetection(frame, corners, ids, min_x, min_y, pixels_per_cm_x, pixels_per_cm_y)
                
                # Check if target reached and continue logic
                allowable_target_range = [
                    (current_target[0] + dx, current_target[1] + dy)
                    for dx in range(-1, 2)
                    for dy in range(-1, 2)
                ]
                
                #check if the target has been reached
                if current_pos in allowable_target_range:     
                                   
                    ret, frame = camera_feed.read()
                    if not ret:
                        print("Failed to capture frame.")
                        break

                
                    # sandworm detection logic
                    worm_trigger = sandwormDetection(ids)
                                        
                    # Handle sandworm presence logic
                    #check if worm trigger is on

                    if worm_trigger == 1:
                        worm_trigger_counter += 1

                        #check if it is the first time the worm trigger has been on
                        if  worm_trigger_counter == 1:

                            #call babySpiceDetection function to get current_pos and current_dir
                            current_pos, current_dir= babySpiceDetection(frame, corners, ids, min_x, min_y, pixels_per_cm_x, pixels_per_cm_y)

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

                    #reset worm trigger counter
                    else:
                        worm_trigger_counter = 0

                    #move on to next point
                    j += 1

                #if the target has not been reached
                else:
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
    mostlyAutomaticMissionControl()


exit()