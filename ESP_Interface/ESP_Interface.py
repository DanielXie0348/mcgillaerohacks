import time
import threading
import keyboard
from ESP_Interface.drone_rc import (
    set_mode, manual_thrusts, set_pitch, set_roll,
    set_yaw, emergency_stop, reset_integral,
    red_LED, green_LED, blue_LED
)

emergency = False
last_send = 0.0
MIN_INTERVAL = 0.05 # seconds

def start():
    set_mode(2)
    set_yaw(0)
    reset_integral()
    red_LED(0) 
    green_LED(1)
    blue_LED(0)
    print("[ESP] Drone Ready")

def trigger_emergency_stop():
    global emergency
    emergency = True
    emergency_stop()

def is_emergency():
    return emergency

def send_commands(thrust, pitch, roll):
    """
    Send thrust + pitch + roll to the drone.
    Rate limited to 20 Hz. Ignored if emergency stop is active.
 
    thrust : 0 to 250   (same on all 4 motors)
    pitch  : -10 to 10  (degrees-ish, forward/back)
    roll   : -10 to 10  (degrees-ish, left/right)
    """
    global last_send
 
    if emergency:
        return
 
    # rate limiter
    now = time.time()
    if now - last_send < MIN_INTERVAL:
        return
    last_send = now
 
    # clamp for safety
    thrust = max(0,   min(250, thrust))
    pitch  = max(-10, min(10,  pitch))
    roll   = max(-10, min(10,  roll))
 
    manual_thrusts(thrust, thrust, thrust, thrust)
    set_pitch(pitch)
    set_roll(roll)
 
def takeoff(hover_thrust=185): # Take off sequence, slowly ramping up thrust to avoid flipping over. Adjust hover_thrust as needed.
    print("[ESP] Taking off...")
    blue_LED(1)
    green_LED(0)
 
    for t in range(100, hover_thrust, 3):
        if emergency:
            return
        manual_thrusts(t, t, t, t)
        time.sleep(0.1)
 
    green_LED(1)
    blue_LED(0)
    print(f"[ESP] Airborne — holding thrust {hover_thrust}")
 
# ─────────────────────────────────────────
# SPACE key listener (runs in background)
# ─────────────────────────────────────────
def _watch_keyboard():
    keyboard.wait("space")
    trigger_emergency_stop()
 
def start_keyboard_listener():
    t = threading.Thread(target=_watch_keyboard, daemon=True)
    t.start()
    print("[ESP] SPACE key emergency stop armed")