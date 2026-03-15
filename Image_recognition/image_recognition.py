import cv2

# tune this on competition day
# lower if drone not detected, raise if false detections
BRIGHTNESS_THRESHOLD = 200

def find_drone(frame):
    """
    Find drone in frame using LED brightness.
    Returns (pixel_x, pixel_y) or None if not found.
    """
    if frame is None:
        return None

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, BRIGHTNESS_THRESHOLD, 255, cv2.THRESH_BINARY)

    moments = cv2.moments(thresh)

    if moments["m00"] == 0:
        return None

    px = moments["m10"] / moments["m00"]
    py = moments["m01"] / moments["m00"]

    return px, py

"""import cv2
import queue
import threading
from inference_sdk import InferenceHTTPClient
from inference_sdk.webrtc import WebcamSource, StreamConfig, VideoMetadata

#Shared frame buffer
frame_queue = queue.Queue(maxsize=1)

client = InferenceHTTPClient.init(
    api_url="https://serverless.roboflow.com/",
    api_key="niXh5ND3br976W7fHDu3"
)

source = WebcamSource(resolution=(640, 480))

config = StreamConfig(
    stream_output=["visualization"],   # exact workflow video output name
    data_output=["predictions"],                # optional, exact data output name
    processing_timeout=3600,
    requested_plan="webrtc-gpu-medium",
    requested_region="us"
)

session = client.webrtc.stream(
    source=source,
    workflow="find-drones",
    workspace="dylans-workspace-nbljz",
    image_input="image",
    config=config
)

@session.on_frame
def on_frame(frame, metadata):
    # Keep only the newest frame so GUI stays responsive
    while not frame_queue.empty():
        try:
            frame_queue.get_nowait()
        except queue.Empty:
            break

    try:
        frame_queue.put_nowait(frame.copy())
    except queue.Full:
        pass
@session.on_data()


def on_data(data: dict, metadata: VideoMetadata):
    
    print(type(data))
    print(data)
    # print(f"Frame {metadata.frame_id}: {data}")

  

def run_stream():
    try:
        session.run()
    except Exception as e:
        print("Stream error:", e)

#Start stream in background
thread = threading.Thread(target=run_stream, daemon=True)
thread.start()

cv2.namedWindow("Workflow Output", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Workflow Output", 1280, 720)

try:
    while True:
        try:
            frame = frame_queue.get(timeout=0.03)
            cv2.imshow("Workflow Output", frame)
        except queue.Empty:
            pass

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            session.close()
            break

        # Handle user closing the window
        if cv2.getWindowProperty("Workflow Output", cv2.WND_PROP_VISIBLE) < 1:
            session.close()
            break

finally:
    cv2.destroyAllWindows()
"""