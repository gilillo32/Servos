import customtkinter as ctk
from gui import ServoControllerApp
from servo import Servo
from servo_collection import ServoCollectionSingleton

if __name__ == "__main__":
    servo_1 = Servo(12, 0)
    servo_2 = Servo(14, 1)

    servo_1.sequence = [12, 14, 15, 16, 17, 20]
    servo_2.sequence = [20, 14, 26, 23, 5, 2]
    servo_collection = ServoCollectionSingleton()
    servo_collection.add_servo(servo_1)
    servo_collection.add_servo(servo_2)
    servo_collection.waiting_sequence = [10, 5, 5, 5, 5, 5]

    root = ctk.CTk()
    app = ServoControllerApp(root)
    root.mainloop()

