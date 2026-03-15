import cv2
from Image_recognition.image_recognition import find_drone

# ─────────────────────────────────────────
# Calibration — measure on competition day
# ─────────────────────────────────────────
CAGE_SIZE_METRES = 1.0

# how many pixels does the cage span in each camera?
# measure this by looking at the feed before flying
CAGE_PIXELS_A_X = 640
CAGE_PIXELS_A_Y = 480
CAGE_PIXELS_B_X = 640
CAGE_PIXELS_B_Y = 480

CAGE_CENTRE_A_X = CAGE_PIXELS_A_X / 2
CAGE_CENTRE_B_X = CAGE_PIXELS_B_X / 2
CAGE_BOTTOM_A_Y = CAGE_PIXELS_A_Y
CAGE_BOTTOM_B_Y = CAGE_PIXELS_B_Y

SCALE_A_X = CAGE_SIZE_METRES / CAGE_PIXELS_A_X
SCALE_A_Y = CAGE_SIZE_METRES / CAGE_PIXELS_A_Y
SCALE_B_X = CAGE_SIZE_METRES / CAGE_PIXELS_B_X
SCALE_B_Y = CAGE_SIZE_METRES / CAGE_PIXELS_B_Y

# last known position fallback
_last_x = 0.0
_last_y = 0.0
_last_z = 0.0

# open cameras
cap_a = cv2.VideoCapture(0)   # side camera → x, z
cap_b = cv2.VideoCapture(1)   # front camera → y, z

def get_position():
    """
    Returns (x, y, z) in metres.
    Origin = cage centre = 0.5m height.
    Target = (0.0, 0.0, 0.0)
    """
    global _last_x, _last_y, _last_z

    ret_a, frame_a = cap_a.read()
    ret_b, frame_b = cap_b.read()

    if not ret_a or not ret_b:
        return _last_x, _last_y, _last_z

    pos_a = find_drone(frame_a)
    pos_b = find_drone(frame_b)

    if pos_a is None and pos_b is None:
        return _last_x, _last_y, _last_z

    # camera A → x and z
    if pos_a is not None:
        px_a, py_a = pos_a
        x   = (px_a - CAGE_CENTRE_A_X) * SCALE_A_X
        z_a = (CAGE_BOTTOM_A_Y - py_a) * SCALE_A_Y
    else:
        x   = _last_x
        z_a = None

    # camera B → y and z
    if pos_b is not None:
        px_b, py_b = pos_b
        y   = (px_b - CAGE_CENTRE_B_X) * SCALE_B_X
        z_b = (CAGE_BOTTOM_B_Y - py_b) * SCALE_B_Y
    else:
        y   = _last_y
        z_b = None

    # average z from both cameras
    if z_a is not None and z_b is not None:
        z_raw = (z_a + z_b) / 2
    elif z_a is not None:
        z_raw = z_a
    elif z_b is not None:
        z_raw = z_b
    else:
        z_raw = _last_z + (CAGE_SIZE_METRES / 2)

    # origin is cage centre so subtract half cage height
    z = z_raw - (CAGE_SIZE_METRES / 2)

    _last_x, _last_y, _last_z = x, y, z
    return x, y, z