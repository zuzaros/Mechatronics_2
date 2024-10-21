import cv2
import numpy as np
import cv2.aruco as aruco
from captureImage import captureImage
from detectMarkers import detectMarkers
import time

def create_grid_map():
    # Set constants for real-world sizes

    grid_size = 5 # cm, side length of each square in the grid


    # Capture an image from the camera and process it
    sharpened_frame = captureImage()

    # Check if captured_image is None
    if sharpened_frame is None:
        print("Error: No image captured")
        return

    # Convert the captured image to grayscale
    gray = cv2.cvtColor(sharpened_frame, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to get a binary image for grid classification
    _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)  # Lower threshold value

    # Create window
    cv2.namedWindow("Binary Feed", cv2.WINDOW_NORMAL)

    # Display the binary image in a loop
    while True:
        cv2.imshow("Binary Feed", binary)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Break windows
    cv2.destroyAllWindows()

    # Detect ArUco markers in the original grayscale image
    corners, ids, tvecs = detectMarkers(gray)

    # Ensure all corner markers (0,1,2,3) are detected
    required_markers = [0, 1, 2, 3]
    highground_markers = [6, 7, 8, 9]
    if ids is None:
        print("No markers detected.")
        return None

    detected_markers = set(ids.flatten())
    print("Detected markers:", detected_markers)    # Debugging: Print the detected markers

    if not all(marker in detected_markers for marker in required_markers):
        print("Not all required corner markers found.")
        return None

# Create a dictionary to hold marker positions and corners
    marker_positions = {}
    aruco_corners = {}

    for i, marker_id in enumerate(ids.flatten()):
        marker_positions[marker_id] = tvecs[i][0]  # Translation vector
        aruco_corners[marker_id] = corners[i][0]   # Corners of the marker

    # Calculate pixel distances and pixels per cm
    def pixel_distance_between_markers(marker_a, marker_b):
        corner_a = aruco_corners[marker_a]
        corner_b = aruco_corners[marker_b]
        return np.linalg.norm(corner_a.mean(axis=0) - corner_b.mean(axis=0))

    width = np.linalg.norm(marker_positions[3] - marker_positions[2]) / 10
    pixel_width = pixel_distance_between_markers(3, 2)
    height = np.linalg.norm(marker_positions[3] - marker_positions[1]) / 10
    pixel_height = pixel_distance_between_markers(3, 1)

    print("Width:", width)  # Debugging: Print the width of the bounding box
    print("Height:", height)  # Debugging: Print the height of the bounding box

    pixels_per_cm_x = pixel_width / width
    pixels_per_cm_y = pixel_height / height

    # calculate 5cm distance in pixels
    five_cm_x = 5 * pixels_per_cm_x
    five_cm_y = 5 * pixels_per_cm_y

    # Set the minimum and maximum x and y values as center of the markers then subtract 5cm (half marker size)
    # min x is the minimum x value of markers 1 and 3
    min_x = min(marker_positions[1][0], marker_positions[3][0]) - five_cm_x
    # min y is the minimum y value of markers 0 and 1
    min_y = min(marker_positions[0][1], marker_positions[1][1]) - five_cm_y
    
    # Adjust the number of grid columns and rows dynamically based on the bounding box
    grid_cols = int((pixel_width) / (grid_size * pixels_per_cm_x)) + 10
    grid_rows = int((pixel_height) / (grid_size * pixels_per_cm_y)) + 10

    print("Grid columns:", grid_cols)  # Debugging: Print the number of grid columns
    print("Grid rows:", grid_rows)      # Debugging: Print the number of grid rows
    
    map_grid = np.zeros((grid_rows, grid_cols), dtype=np.uint8)

    def classify_pixel_area(binary_image, x, y, cell_size, aruco_corners, highground_markers):
        if x < 0 or y < 0 or x + cell_size > binary_image.shape[1] or y + cell_size > binary_image.shape[0]:
            return 0  # Default to sand if out of bounds

        roi = binary_image[y:y + cell_size, x:x + cell_size]
        avg_intensity = np.mean(roi)

        for marker_id, corners in aruco_corners.items():
            x_min, x_max = corners[:, 0].min(), corners[:, 0].max()
            y_min, y_max = corners[:, 1].min(), corners[:, 1].max()
            if x < x_max and x + cell_size > x_min and y < y_max and y + cell_size > y_min:
                if marker_id in highground_markers:
                    return 1  # Highground marker
                else:
                    return 3  # ArUco marker

        return 2 if avg_intensity > 128 else 0  # Spice or sand

    for row in range(grid_rows):
        for col in range(grid_cols):
            x = int((col * grid_size * pixels_per_cm_x))
            y = int((row * grid_size * pixels_per_cm_y))
            map_grid[row, col] = classify_pixel_area(binary, x, y, int(grid_size * pixels_per_cm_x), aruco_corners, highground_markers)

    # Display the generated map (for visualization, using 255 for spice, 128 for highground, 64 for aruco marker, and 0 for sand)
    map_image = np.zeros((grid_rows, grid_cols), dtype=np.uint8)
    map_image[map_grid == 2] = 255  # Spice
    map_image[map_grid == 1] = 128  # Highground
    map_image[map_grid == 3] = 64   # ArUco marker
    map_image[map_grid == 0] = 0    # Sand

    # Resize for better visualization
    scaling_factor = 20  # Increase the scaling factor for better visualization
    resized_map = cv2.resize(map_image, (grid_cols * scaling_factor, grid_rows * scaling_factor), interpolation=cv2.INTER_NEAREST)

    # Apply a colormap for better visualization
    colored_map = cv2.applyColorMap(resized_map, cv2.COLORMAP_JET)

    # Show the final classified map
    cv2.imshow("Classified Map", colored_map)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Print the map grid (for debugging purposes)
    print("Generated map grid (2=spice, 1=highground, 3=aruco marker, 0=sand):")
    print(map_grid)

    # Return the map grid
    return map_grid, pixels_per_cm_x, pixels_per_cm_y, min_x, min_y

if __name__ == "__main__":
    create_grid_map()
