import cv2
import numpy as np

from captureImage import captureImage
from detectMarkers import detectMarkers

def create_grid_map():
    # Set constants for real-world sizes
    aruco_marker_size = 10  # cm, side length of each ArUco marker
    grid_size = 5  # cm, side length of each square in the grid

    # Known dimensions of the map in cm
    real_width = 75  # cm
    real_height = 75  # cm

    # Capture an image from the camera and process it
    captured_image = captureImage()

    # Check if captured_image is None
    if captured_image is None:
        print("Failed to capture image.")
        return None

    # Convert the captured image to grayscale
    gray = cv2.cvtColor(captured_image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to get a binary image for grid classification
    _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)  # Lower threshold value

    # Create window
    cv2.namedWindow("Binary Feed", cv2.WINDOW_NORMAL)

    # Display the binary image in a loop
    while True:
        # Display the resulting frame
        cv2.imshow('Binary Feed', binary)
        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Break windows
    cv2.destroyAllWindows()

    # Detect ArUco markers in the original grayscale image
    corners, ids = detectMarkers(gray)

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

    # Calculate real-world positions of the centers of the markers based on marker IDs
    center_positions = {}
    for corner, marker_id in zip(corners, ids.flatten()):
        if marker_id in required_markers + highground_markers:
            if corner[0].size == 0:
                print(f"Marker {marker_id} has no valid corners.")
                return None
            # Use the mean of the corner points to get the center position of the marker
            center_positions[marker_id] = np.mean(corner[0], axis=0)

    # Check if all required markers have valid center positions
    if not all(marker in center_positions for marker in required_markers):
        print("Not all required markers have valid center positions.")
        return None

    # Calculate pixels per cm in x and y directions using the known size of the ArUco markers
    def calculate_pixels_per_cm(corner):
        if len(corner[0]) < 2:
            print("Not enough points to calculate pixels per cm.")
            return None
        # Calculate the distance between two adjacent corners of the same marker
        side_length_in_pixels = np.linalg.norm(corner[0][0] - corner[0][1])
        return side_length_in_pixels / aruco_marker_size

    # Use one of the detected markers to calculate pixels per cm
    pixels_per_cm_x = calculate_pixels_per_cm(corners[0])
    pixels_per_cm_y = calculate_pixels_per_cm(corners[0])

    if pixels_per_cm_x is None or pixels_per_cm_y is None:
        print("Failed to calculate pixels per cm.")
        return None

    # Calculate half marker for extremities of the ArUco markers
    half_marker_size = aruco_marker_size / 2

    # Adjust the bounding box to include the extremities of the markers
    min_x = int(np.min([corner[0][:, 0].min() for corner in corners]) - half_marker_size * pixels_per_cm_x)
    max_x = int(np.max([corner[0][:, 0].max() for corner in corners]) + half_marker_size * pixels_per_cm_x)
    min_y = int(np.min([corner[0][:, 1].min() for corner in corners]) - half_marker_size * pixels_per_cm_y)
    max_y = int(np.max([corner[0][:, 1].max() for corner in corners]) + half_marker_size * pixels_per_cm_y)

    # Calculate the number of grid cells in the x and y directions based on the real-world size
    grid_cols = int(real_width / grid_size)
    grid_rows = int(real_height / grid_size)

    # Create a map grid 
    map_grid = np.zeros((grid_rows, grid_cols), dtype=np.uint8)

    # Function to classify a pixel area as "spice", "sand", or "aruco marker" based on the binary image
    def classify_pixel_area(binary_image, x, y, cell_size, aruco_corners, highground_markers):
        # Extract the region of interest (ROI) from the binary image for each grid cell
        roi = binary_image[y:y + cell_size, x:x + cell_size]
        avg_intensity = np.mean(roi)
        
        # Check if the cell overlaps with any ArUco marker
        for marker_id, corners in aruco_corners.items():
            if (x < corners[:, 0].max() and x + cell_size > corners[:, 0].min() and
                y < corners[:, 1].max() and y + cell_size > corners[:, 1].min()):
                if marker_id in highground_markers:
                    return 1  # Highground marker
                else:
                    return 3  # ArUco marker

        # Classification based on intensity: light = spice (2), dark = sand (0)
        if avg_intensity > 128:
            return 2  # Spice (white)
        else:
            return 0  # Sand (dark)

    # Fill the map grid by classifying each 5x5 cm square
    aruco_corners = {marker_id: corner[0] for corner, marker_id in zip(corners, ids.flatten())}
    for row in range(grid_rows):
        for col in range(grid_cols):
            # Convert grid cell position to pixel coordinates
            x_pixel = int(min_x + col * pixels_per_cm_x * grid_size)
            y_pixel = int(min_y + row * pixels_per_cm_y * grid_size)
            
            # Classify the pixel area corresponding to this grid cell
            cell_size = int(pixels_per_cm_x * grid_size)
            map_grid[row, col] = classify_pixel_area(binary, x_pixel, y_pixel, cell_size, aruco_corners, highground_markers)

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

    # Save the final classified map to a file
    output_filename = "classified_map.png"
    cv2.imwrite(output_filename, colored_map)
    print(f"Classified map saved to {output_filename}")

    # Show the final classified map
    cv2.imshow("Classified Map", colored_map)

    # Keep the binary image window open for debugging
    cv2.imshow('Binary Feed', binary)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Print the map grid (for debugging purposes)
    print("Generated map grid (2=spice, 1=highground, 3=aruco marker, 0=sand):")
    print(map_grid)

    # Return the map grid
    return map_grid, pixels_per_cm_x, pixels_per_cm_y, min_x, min_y

if __name__ == "__main__":
    create_grid_map()
