from Controller.pid import PIDController

# Altitude PID (z → thrust)
altitude_pid = PIDController(
    kp=35, ki=2.5, kd=18,
    setpoint=0.0,           # 0 = cage centre = 0.5m from floor
    hover_throttle=185,     # tune on the day
    output_min=0,
    output_max=250          # drone max is 250
)

# X position PID (x → pitch)
x_pid = PIDController(
    kp=2, ki=0.0, kd=1,
    setpoint=0.0,
    hover_throttle=0,
    output_min=-10,
    output_max=10
)

# Y position PID (y → roll)
y_pid = PIDController(
    kp=2, ki=0.0, kd=1,
    setpoint=0.0,
    hover_throttle=0,
    output_min=-10,
    output_max=10
)

def compute_commands(x, y, z, dt):
    thrust = altitude_pid.update(z)   # z → thrust
    pitch  = x_pid.update(x)          # x → pitch
    roll   = y_pid.update(y)          # y → roll
    return thrust, pitch, roll