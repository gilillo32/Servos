import time


class Servo:
    min_angle = 0
    max_angle = 2100
    my_channel = -1

    def __init__(self, pin, p_id, channel, pwm, rasp=False):
        self.pin = pin
        self.id = p_id
        self.my_channel = channel
        self.pwm = pwm
        self.sequence = []
        self.min_limit = 500
        self.max_limit = 2100
        self.rasp = rasp
        self.description = "Labio inf." if p_id == 1 else "Labio sup." if p_id == 2 else "Otro"

    def move(self, angle):
        if angle < self.min_angle or angle > self.max_angle:
            raise ValueError(f"El valor debe estar entre {self.min_angle} y {self.max_angle}")
        else:
            print("[INFO] Moving servo " + str(self.id) + " to position: " + str(angle))
            if self.rasp:
                self.pwm.set_pulse_width(self.my_channel, angle)
