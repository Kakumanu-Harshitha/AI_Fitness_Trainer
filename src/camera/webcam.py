import cv2

def open_camera(cam_index=0):
    cap = cv2.VideoCapture(cam_index)

    # Set higher resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    return cap


def read_frame(cap):
    return cap.read()


def release_camera(cap):
    cap.release()
    cv2.destroyAllWindows()
