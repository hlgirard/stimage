from time import sleep
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

# Connect to the motor kit HAT
kit = MotorKit()

# Get reference to stepper 1
stp = kit.stepper2

# One complete revolution (200 steps)
for i in range(200):
    stp.onestep()
    sleep(0.01)

# One revolution backwards (200 steps)
for i in range(200):
    stp.onestep(direction=stepper.BACKWARD)
    sleep(0.01)

# Bunch of interleaved steps
for i in range(400):
    stp.onestep(style=stepper.INTERLEAVE)
    sleep(0.01)

# Release stepper
stp.release()