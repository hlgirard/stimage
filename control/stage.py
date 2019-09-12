'''
Custom object to control a stepper motor-based XY stage
'''

import logging

from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
from gpiozero import Button

class Stage:
    '''XY stage control with stepper motors'''

    def __init__(self):
        '''Initialize stepper motors and get references to limit switches'''

        # Get references to stepper motors
        self.kit = MotorKit()
        self.stepperX = self.kit.stepper1
        self.stepperY = self.kit.stepper2

        # Release the steppers to start
        self.stepperX.release()
        self.stepperY.release()

        # Get reference to limit buttons
        self.limXMaxBut = Button(4, bounce_time=0.05)
        self.limYMinBut = Button(5, bounce_time=0.05)

        # Initialize position variables
        self.posX = 0
        self.posY = 0

        # Axis length
        self.maxX = 39000 # X-axis length
        self.maxY = 23000 # Y-axis length

        # Initialization interlock
        self.is_initialized_x = False
        self.is_initialized_y = False

    def __del__(self):
        '''Releases stepper motors on destroy'''
        logging.debug("Destroying Stage object. Releasing both steppers.")
        self.stepperX.release()
        self.stepperY.release()

    def initialize_stage(self, x_only=False):

        logging.info("Initializing stage.")

        # Initialize X axis
        while not self.limXMaxBut.is_pressed:
            self.moveX(200, override=True)
        self.moveX(-800, override=True)
        self.posX = self.maxX

        self.is_initialized_x = True


        # Initialize Y axis
        if not x_only:
            while not self.limYMinBut.is_pressed:
                self.moveY(-200, override=True)
            self.moveY(800, override=True)
            self.posY = 0

            self.is_initialized_y = True

        logging.info("Stage initialized")


    def goto(self, x, y):
        '''Move to position x, y'''

        if not self._check_move_valid(x, y):
            return

        logging.debug("Moving to position %d, %d", x, y)

        # Move X axis
        self.moveX(x-self.posX)

        # Move Y axis
        self.moveY(y-self.posY)


    def moveX(self, n_steps, override=False):
        '''Move stage along the X axis for n_steps'''

        if not override:
            if not self._check_move_valid(self.posX + n_steps, self.posY):
                return

        try:
            if n_steps > 0:
                for _ in range(n_steps):
                    self.stepperX.onestep(style=stepper.INTERLEAVE)
                    self.posX += 1

            if n_steps < 0:
                for _ in range(-1 * n_steps):
                    self.stepperX.onestep(style=stepper.INTERLEAVE, direction=stepper.BACKWARD)
                    self.posX += -1

        finally:
            self.stepperX.release()

    def moveY(self, n_steps, override=False):
        '''Move stage along the Y axis for n_steps'''

        if not override:
            if not self._check_move_valid(self.posX, self.posY + n_steps):
                return

        try:
            if n_steps > 0:
                for _ in range(n_steps):
                    self.stepperY.onestep(style=stepper.INTERLEAVE)
                    self.posY += 1

            if n_steps < 0:
                for _ in range(-1 * n_steps):
                    self.stepperY.onestep(style=stepper.INTERLEAVE, direction=stepper.BACKWARD)
                    self.posY += -1

        finally:
            self.stepperY.release()

    def release(self):
        '''Releases all the stepper motors'''

        logging.debug("Released both steppers")
        self.stepperX.release()
        self.stepperY.release()

    def _check_move_valid(self, newX, newY):
        '''Make sure stage is initialized and requested position is within the bounds'''

        if (newX != self.posX) and not self.is_initialized_x:
            logging.warning("Illegal motion: X-axis is not initialized.")
            return False

        if (newY != self.posY) and not self.is_initialized_y:
            logging.warning("Illegal motion: Y-axis is not initialized.")
            return False

        if newX > self.maxX or newX < 0 or newY > self.maxY or newY < 0:
            logging.warning("Illegal motion: Requested position out of bounds.")
            return False

        return True

    def _safe_shutdown(self):
        '''Release both steppers and raise an error'''

        self.stepperX.release()
        self.stepperY.release()
        raise IOError("An error has occured, shutting down stage.")
