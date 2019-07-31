import logging
from time import sleep

from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
from gpiozero import Button


class Stage:

    def __init__(self):
        
        # Get references to stepper motors
        self.kit = MotorKit()
        self.stepperX = self.kit.stepper1
        self.stepperY = self.kit.stepper2

        # Release the steppers
        self.stepperX.release()
        self.stepperY.release()

        # Get reference to limit buttons
        self.limXMaxBut = Button(4, bounce_time=0.05)
        self.limYMaxBut = Button(5, bounce_time=0.05)

        # Initialize position variables
        self.posX = 0
        self.posY = 0

        # Safety limits
        self.maxX = 40000 # X-axis length
        self.maxY = 30000 # Y-axis length

    def initialize_stage(self):

        # Initialize X axis
        while not self.limXMaxBut.is_pressed:
            self.stepperX.onestep()
        self.posX = 0

        # Initialize Y axis
        while not self.limYMaxBut.is_pressed:
            self.stepperY.onestep()
        self.posY = 0


    def goto(self, x, y):
        '''Move to position x, y'''

        # Make sure requested position is within limits
        if x > self.maxX or y > self.maxY:
            print("Requested position outside limits")
            return

        # Move X axis
        if self.posX < x:
            while self.posX < x:
                self.moveX(1)
        elif self.posX > x:
            while self.posX > x:
                self.moveX(-1)
        else:
            pass

        # Move Y axis
        if self.posY < y:
            while self.posY < y:
                self.moveY(1)
        elif self.posY > y:
            while self.posY > y:
                self.moveY(-1)
        else:
            pass

    def moveX(self, n_steps):
        '''Move stage along the X axis for n_steps'''
        
        if n_steps > 0:
            for _ in range(n_steps):
                self.stepperX.onestep(style=stepper.INTERLEAVE)
                self.posX += 1

        if n_steps < 0:
            for _ in range(-1 * n_steps):
                self.stepperX.onestep(style=stepper.INTERLEAVE, direction=stepper.BACKWARD)
                self.posX += -1

        self.stepperX.release()

    def moveY(self, n_steps):
        '''Move stage along the Y axis for n_steps'''

        if n_steps > 0:
            for _ in range(n_steps):
                self.stepperY.onestep(style=stepper.INTERLEAVE)
                self.posY += 1

        if n_steps < 0:
            for _ in range(-1 * n_steps):
                self.stepperY.onestep(style=stepper.INTERLEAVE, direction=stepper.BACKWARD)
                self.posY += -1

        self.stepperY.release()