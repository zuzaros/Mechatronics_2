def objectTracking(ids, corners, marker_id):
    object = None
    if ids is not None:
        for i, id_marker in enumerate(ids.flatten()):
            if id_marker == marker_id:
                object = corners[i]
                print(f"Object {marker_id} found at {object}")
    return object
