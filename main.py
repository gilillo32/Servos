import customtkinter as ctk
import pigpio

from pwm import PWM

from gui.ventana_inicio import VentanaPrincipal
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
    pwm = 0
    # pwm = pi_init()
    servo_1 = Servo(12, 0, 4, pwm)
    servo_2 = Servo(14, 1, 0, pwm)

    servo_collection = ServoCollectionSingleton()
    servo_collection.add_servo(servo_1)
    servo_collection.add_servo(servo_2)
    servo_collection.waiting_sequence = [10, 5, 5, 5, 5, 5]

    root = ctk.CTk()
    root.geometry("500x100")
    app = VentanaPrincipal(root)
    root.mainloop()
