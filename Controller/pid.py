"""
Drone PID Height Controller (Z-axis)
=====================================
Controls motor speed (0–255) based on Z-axis position error.

Tuning values (suggested for a typical 250–500g racing/hobby drone):
  Kp = 35.0  — Proportional gain: main correction force
  Ki =  2.5  — Integral gain: eliminates steady-state error (e.g. hover drift)
  Kd = 18.0  — Derivative gain: dampens oscillation on approach

Adjust guidelines:
  - Increase Kp if the drone responds too slowly to height changes.
  - Decrease Kp if the drone overshoots and oscillates.
  - Increase Ki if the drone never quite reaches the target (steady-state offset).
  - Increase Kd if the drone oscillates even with low Kp.

Motor output:
  - 0   = motors off (free fall)
  - 128 = roughly hover thrust (tune HOVER_THROTTLE for your drone's weight)
  - 255 = full throttle
"""

import time

# ── PID Gains ────────────────────────────────────────────────────────────────
Kp: float = 35.0
Ki: float =  2.5
Kd: float = 18.0

# ── Controller Config ─────────────────────────────────────────────────────────
TARGET_Z: float      = 0     # Desired altitude in metres
HOVER_THROTTLE: int  = 100      # Base motor speed to hover (tune per drone weight)
MOTOR_MIN: int       = 25       # Minimum motor output
MOTOR_MAX: int       = 255      # Maximum motor output

INTEGRAL_LIMIT: float = 30.0    # Anti-windup clamp on integral term


class PIDController:
    """
    A PID controller for single-axis (Z) drone height control.

    Args:
        kp:             Proportional gain
        ki:             Integral gain
        kd:             Derivative gain
        setpoint:       Target altitude (metres)
        hover_throttle: Base throttle offset to maintain hover
        output_min:     Minimum clamped output (motor speed)
        output_max:     Maximum clamped output (motor speed)
        integral_limit: Anti-windup clamp for the integral accumulator
    """

    def __init__(
        self,
        kp: float,
        ki: float,
        kd: float,
        setpoint: float,
        hover_throttle: int = 128,
        output_min: int = 0,
        output_max: int = 255,
        integral_limit: float = 50.0,
    ) -> None:
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.hover_throttle = hover_throttle
        self.output_min = output_min
        self.output_max = output_max
        self.integral_limit = integral_limit

        self._integral: float   = 0.0
        self._prev_error: float = 0.0
        self._prev_time: float  = time.monotonic()

    def update(self, current):
        """
        Compute motor speed given current position.

        Args:
            x: Current X position (unused — reserved for future lateral control)
            y: Current Y position (unused — reserved for future lateral control)
            z: Current Z (altitude) in metres

        Returns:
            Motor speed as an integer in [0, 255]
        """
        now = time.monotonic()
        dt  = now - self._prev_time

        # Guard against zero or negative dt (e.g. first call, clock anomalies)
        if dt <= 0.0:
            dt = 1e-6

        # ── Error ─────────────────────────────────────────────────────────────
        error = self.setpoint - current   # uses whatever you pass in

        # ── Integral with anti-windup ─────────────────────────────────────────
        self._integral += error * dt
        self._integral  = max(
            -self.integral_limit,
            min(self.integral_limit, self._integral)
        )

        # ── Derivative (on measurement, not error, to avoid derivative kick) ──
        derivative = (error - self._prev_error) / dt

        # ── PID output ────────────────────────────────────────────────────────
        pid_output = (
            self.kp * error
            + self.ki * self._integral
            + self.kd * derivative
        )

        # ── Add hover offset and clamp to motor range ─────────────────────────
        raw_motor  = self.hover_throttle + pid_output
        motor_speed = int(max(self.output_min, min(self.output_max, raw_motor)))

        # ── Store state for next iteration ────────────────────────────────────
        self._prev_error = error
        self._prev_time  = now

        return motor_speed

    def reset(self) -> None:
        """Reset integrator and derivative state (use on arm/disarm)."""
        self._integral   = 0.0
        self._prev_error = 0.0
        self._prev_time  = time.monotonic()


# ── Example: Constant Feedback Loop ──────────────────────────────────────────

def get_drone_position() -> tuple[float, float, float]:
    """
    Stub: replace with your actual sensor read (e.g. barometer, rangefinder,
    optical flow, or GPS fused altitude).

    Returns:
        (x, y, z) position in metres
    """
    raise NotImplementedError(
        "Replace get_drone_position() with your sensor interface."
    )


def set_motor_speed(speed: int) -> None:
    """
    Stub: replace with your ESC / motor driver write.
    
    Args:
        speed: PWM value 0–255 sent to all four motors (uniform for Z only)
    """
    raise NotImplementedError(
        "Replace set_motor_speed() with your ESC interface."
    )


def main() -> None:
    pid = PIDController(
        kp=Kp,
        ki=Ki,
        kd=Kd,
        setpoint=TARGET_Z,
        hover_throttle=HOVER_THROTTLE,
        output_min=MOTOR_MIN,
        output_max=MOTOR_MAX,
        integral_limit=INTEGRAL_LIMIT,
    )

    print(f"[PID] Target altitude: {TARGET_Z} m")
    print(f"[PID] Gains — Kp={Kp}  Ki={Ki}  Kd={Kd}")
    print("[PID] Starting control loop. Press Ctrl+C to stop.\n")

    try:
        while True:
            x, y, z = get_drone_position()          # ← sensor read
            motor_speed = pid.update(x, y, z)       # ← PID computation
            set_motor_speed(motor_speed)             # ← actuator write

            print(
                f"z={z:.3f}m  error={TARGET_Z - z:+.3f}m  "
                f"motor={motor_speed}/255"
            )

            # No explicit sleep — assumes your sensor/ESC loop provides timing.
            # Add  time.sleep(0.01)  for a ~100 Hz software cap if needed.

    except KeyboardInterrupt:
        print("\n[PID] Loop stopped. Setting motors to zero.")
        set_motor_speed(0)


if __name__ == "__main__":
    main()