import customtkinter as ctk
from gui import ServoControllerApp

if __name__ == "__main__":
    root = ctk.CTk()
    app = ServoControllerApp(root)
    root.mainloop()
