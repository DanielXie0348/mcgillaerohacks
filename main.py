import time
from Controller.controller import compute_commands
from ESP_Interface.ESP_Interface import (
    start, takeoff, send_commands, is_emergency, start_keyboard_listener
)

def get_position():
    # Placeholder for computer vision code to determine drone's position
    # In a real implementation, this would use OpenCV to process camera input
    return 0,0,0 # x, y, z coordinates

LOOP_HZ     = 20 # Frequency is 20 Hertz
LOOP_PERIOD = 1.0 / LOOP_HZ   # 0.05 seconds

def main():
    print("[MAIN] Starting up")

    start_keyboard_listener()   # arm SPACE key emergency stop
    start()                     # connect, set mode 2
    takeoff()                   # ramp up to hover height

    print("[MAIN] Hovering - press SPACE to emergency stop")

    last_time = time.time()

    while not is_emergency():
        t_start   = time.time()
        dt        = t_start - last_time
        last_time = t_start

        x, y, z = get_position()
        thrust, pitch, roll = compute_commands(x, y, z, dt)
        send_commands(thrust, pitch, roll)

        # 4. debug — remove when flying for real
        print(f"x={x:.2f} y={y:.2f} z={z:.2f} | T={thrust:.0f} p={pitch:.2f} r={roll:.2f}")

        # 5. sleep for remainder of loop period
        elapsed = time.time() - t_start
        time.sleep(max(0, LOOP_PERIOD - elapsed))

    print("[MAIN] Stopped")

if __name__ == "__main__":
    main()
