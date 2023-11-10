import time


class ServoCollectionSingleton:
    _instance = None

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.servo_list = []
            cls._instance.waiting_sequence = []
        return cls._instance

    def add_servo(self, servo):
        self.servo_list.append(servo)

    def set_waiting_sequence(self, waiting_sequence):
        self._instance.waiting_sequence = waiting_sequence

    def search_servo_by_id(self, p_id):
        for servo in self.servo_list:
            if servo.id == p_id:
                return servo
        return None

    def execute_sequence(self):
        current_step = 0
        print("Executing sequence...")
        while current_step < len(self.waiting_sequence):
            print("\n\nCurrent step:", current_step)
            for servo in self.servo_list:
                servo.move(servo.sequence[current_step])
                print(f"Moving {servo.id} {servo.sequence[current_step]} degrees...")
            print(f"Sleeping {self.waiting_sequence[current_step]} seconds...")
            time.sleep(self.waiting_sequence[current_step])
            current_step += 1
