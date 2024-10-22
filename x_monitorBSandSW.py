import cv2
import time
import numpy as np
import cv2.aruco as aruco

# Import the necessary functions
from detectMarkers import detectMarkers
from x_moveToHighground import move_to_highground
from x_followPath import follow_path

def monitor_sandworm_and_babyspice(camera_feed, map_grid, collected_spice, pixels_per_cm_x, pixels_per_cm_y, min_x, min_y):
    last_checked_time = 0  # Initialize last check time
    check_interval = 3  # 3 seconds between checks

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

        # Perform checks and operations only if the interval has passed
        if current_time - last_checked_time >= check_interval:
            last_checked_time = current_time  # Update last check time

            # Check if the sandworm (marker 5) is in frame
            sandworm_present = False
            if ids is not None:
                sandworm_present = 5 in ids.flatten()  # Check for sandworm marker

            if sandworm_present:
                move_to_highground()
            else:
                follow_path()

            # Track BabySpice’s position (marker 4)
            if ids is not None and 4 in ids.flatten():
                marker_index = np.where(ids == 4)[0][0]
                marker_corners = corners[marker_index]

                # Calculate the center of the detected marker
                marker_center = np.mean(marker_corners[0], axis=0)
                marker_x, marker_y = int(marker_center[0]), int(marker_center[1])

                print(f"BabySpice's position: (X: {marker_x}, Y: {marker_y})")

                # Convert pixel position to grid coordinates
                grid_x = int((marker_x - min_x) / (pixels_per_cm_x * 5))  # grid_size is 5 cm
                grid_y = int((marker_y - min_y) / (pixels_per_cm_y * 5))

                print(f"BabySpice's grid position: (Row: {grid_y}, Col: {grid_x})")

                if map_grid[grid_y, grid_x] == 2:  # If BabySpice is on a spice cell
                    collected_spice.add((grid_y, grid_x))  # Mark spice cell as collected
                    print(f"Spice collected at grid position: ({grid_y}, {grid_x})")

                # Calculate the orientation of the marker
                # The orientation can be determined by the angle of the line connecting two corners
                corner_0 = marker_corners[0][0]  # First corner
                corner_1 = marker_corners[0][1]  # Second corner
                dx = corner_1[0] - corner_0[0]
                dy = corner_1[1] - corner_0[1]
                angle = np.degrees(np.arctan2(dy, dx))

                print(f"BabySpice's orientation: {angle:.2f} degrees")
            else:
                print("BabySpice not detected.")

            # Check if all spice is collected
            spice_cells = np.argwhere(map_grid == 2)
            all_spice_collected = all(tuple(cell) in collected_spice for cell in spice_cells)

            if all_spice_collected:
                print('All spice collected. Mission complete!')
                break

    
        # Display the frame with detected markers and grid lines
        if ids is not None:
            aruco.drawDetectedMarkers(frame, corners, ids)
        cv2.imshow('Mission Control Feed', frame)

        # Break the loop if the user presses 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release camera feed and close all OpenCV windows
    camera_feed.release()
    cv2.destroyAllWindows()
