import cv2

cap_a = cv2.VideoCapture(0)   # side camera (gives x, z)
cap_b = cv2.VideoCapture(1)   # front camera (gives y, z)

def get_frames():
    ret_a, frame_a = cap_a.read()
    ret_b, frame_b = cap_b.read()

    if not ret_a or not ret_b:
        return None, None

    return frame_a, frame_b

def release():
    cap_a.release()
    cap_b.release()
