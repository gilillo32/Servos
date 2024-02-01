import time


class Servo:
    min_angle = 0
    max_angle = 2500
    my_channel = -1

    def __init__(self, pin, p_id, channel, pwm, rasp=False):
        self.pin = pin
        self.id = p_id
        self.my_channel = channel
        self.pwm = pwm
        self.sequence = []
        self.min_limit = -1
        self.max_limit = -1
        self.rasp = rasp

    def move(self, angle):
        if angle < self.min_angle or angle > self.max_angle:
            raise ValueError(f"El ángulo debe estar entre {self.min_angle} y {self.max_angle}")
        else:
            print("Moving servo " + str(self.id) + " to position: " + str(angle))
            if self.rasp:
                self.pwm.set_pulse_width(self.my_channel, angle)
