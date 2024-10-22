HIGHGROUND_MARKERS = [2, 3, 5]  # Pre-defined highground markers

def identifyHighground(ids, corners):
    highground = []
    if ids is not None:
        for i, marker_id in enumerate(ids.flatten()):
            if marker_id in HIGHGROUND_MARKERS:
                highground.append(corners[i])
    return highground
