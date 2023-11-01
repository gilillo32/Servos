class Servo:
    min_angle = 0
    max_angle = 180

    def __init__(self, pin, id):
        self.pin = pin
        self.id = id
        self.sequence = []

    def move(self, angle):
        if angle < self.min_angle or angle > self.max_angle:
            raise ValueError(f"El ángulo debe estar entre {self.min_angle} y {self.max_angle}")
        else:
            print(f"Servomotor {self.id}: {angle}")
