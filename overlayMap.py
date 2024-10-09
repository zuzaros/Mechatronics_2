import cv2

def overlayMap(frame, map_data):
    babySpice = map_data.get('babySpice', [])
    sandworm = map_data.get('sandworm', [])

    # Overlay babySpice and sandworm on the frame if they are not empty
    if babySpice and isinstance(babySpice, list) and all(isinstance(i, list) and len(i) == 2 for i in babySpice):
        for (x, y) in babySpice:
            cv2.circle(frame, (x, y), 100, (255, 0, 0), -1)  
    if sandworm and isinstance(sandworm, list) and all(isinstance(i, list) and len(i) == 2 for i in sandworm):
        for (x, y) in sandworm:
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
