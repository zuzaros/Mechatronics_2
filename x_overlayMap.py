import cv2

def overlayMap(frame, map_data):
    babySpice = map_data.get('babySpice', [])
    sandworm = map_data.get('sandworm', [])

    # The two objects are the corners of the ArUco markers on the image plane
    # We need to find the point in the middle of the first and the third corner to overlay the object
    # Check if babySpice and sandworm are not empty and are lists
    if babySpice and isinstance(babySpice, list):
        for i in babySpice:
            babySpicecircle = [(int((i[0][0][0] + i[0][2][0]) / 2), int((i[0][0][1] + i[0][2][1]) / 2))]
                               
    if sandworm and isinstance(sandworm, list):
        for i in sandworm:
            sandwormcircle = [(int((i[0][0][0] + i[0][2][0]) / 2), int((i[0][0][1] + i[0][2][1]) / 2))]

    # Overlay babySpice and sandworm on the frame if they are not empty
    if babySpicecircle and isinstance(babySpicecircle, list) and all(len(i) == 2 for i in babySpicecircle):
        for (x, y) in babySpicecircle:
            cv2.circle(frame, (x, y), 100, (255, 0, 0), -1)  
    if sandwormcircle and isinstance(sandwormcircle, list) and all(len(i) == 2 for i in sandwormcircle):
        for (x, y) in sandwormcircle:
            cv2.circle(frame, (x, y), 100, (0, 0, 255), -1)  

    return frame

if __name__ == "__main__":
    # Test overlayMap function
    frame = cv2.imread("sample.jpg")
    map_data = {
        'babySpice': [[100, 100]],
        'sandworm': [[200, 200]]
    }
    overlay_frame = overlayMap(frame, map_data)
    cv2.imshow("Overlay Frame", overlay_frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
