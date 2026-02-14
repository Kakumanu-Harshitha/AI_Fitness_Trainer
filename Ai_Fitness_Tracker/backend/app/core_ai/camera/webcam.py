import cv2


def open_camera(cam_index=0):
    # Try with CAP_DSHOW on Windows for faster initialization and better compatibility
    try:
        cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
        if cap.isOpened():
            # Set higher resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            return cap
    except:
        pass  # Fall back to default if DSHOW fails
    
    # Fallback to default if DSHOW fails
    cap = cv2.VideoCapture(cam_index)
    if cap.isOpened():
        # Set higher resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    return cap


def read_frame(cap):
    return cap.read()


def release_camera(cap):
    cap.release()