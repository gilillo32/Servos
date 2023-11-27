import customtkinter as ctk
import pigpio

from gui import ServoControllerApp
from pwm import PWM
from servo import Servo
from servo_collection import ServoCollectionSingleton


def pi_init():
    # PI init:
    pi = pigpio.pi()

    if not pi.connected:
        exit(0)

    custom_pwm = PWM(pi)  # defaults to bus 1, address 0x40

    custom_pwm.set_frequency(50)

    return custom_pwm


if __name__ == "__main__":
    pwm = pi_init()

    servo_1 = Servo(12, 0, 4, pwm)
    servo_2 = Servo(14, 1, 0, pwm)

    servo_1.sequence = [12, 14, 15, 16, 17, 20]
    servo_2.sequence = [20, 14, 26, 23, 5, 2]
    servo_collection = ServoCollectionSingleton()
    servo_collection.add_servo(servo_1)
    servo_collection.add_servo(servo_2)
    servo_collection.waiting_sequence = [10, 5, 5, 5, 5, 5]

    root = ctk.CTk()
    app = ServoControllerApp(root)
    root.mainloop()
