import time


class ServoCollection:
    def __init__(self, servo_list):
        self.servo_list = servo_list
        self.waiting_sequence = []

    def search_servo_by_id(self, p_id):
        for servo in self.servo_list:
            if servo.id == p_id:
                return servo
        return None

    def execute_sequence(self):
        current_step = 0
        while current_step < len(self.waiting_sequence):
            for servo in self.servo_list:
                servo.move(servo.sequence[current_step])
            time.sleep(self.waiting_sequence[current_step])

