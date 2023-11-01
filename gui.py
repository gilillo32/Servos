import tkinter as tk
import customtkinter as ctk


class ServoControllerApp:
    def __init__(self, master):
        self.master = master
        master.title("Controlador de Servomotores")

        self.servo_count_label = tk.Label(master, text="Número de Servomotores:")
        self.servo_count_label.pack()

        self.servo_count_var = tk.StringVar(value="2")

        values_str = list(map(str, [2, 3]))

        self.servo_count_combobox = ctk.CTkComboBox(master, values=values_str, command=self.on_combobox_change)
        self.servo_count_combobox.pack()

        self.sequence_entries = []
        print(self.servo_count_var.get())
        for i in range(int(self.servo_count_var.get())):
            self.create_servo_sequence_entry(i + 1)

        self.submit_button = tk.Button(master, text="Ejecutar", command=self.execute_sequence)
        self.submit_button.pack()

    def create_servo_sequence_entry(self, servo_number):
        label = tk.Label(self.master, text=f"Secuencia para Servomotor {servo_number}:")

        entry = tk.Entry(self.master)
        label.pack()
        entry.pack()

    def execute_sequence(self):
        servo_count = int(self.servo_count_var.get())

        for i in range(servo_count):
            sequence = self.sequence_entries[i].get()
            print(f"Servomotor {i + 1}: {sequence}")

    def on_combobox_change(self, event):
        for widgets in self.master.winfo_children():
            if widgets != self.servo_count_label and widgets != self.servo_count_combobox and widgets != self.submit_button:
                widgets.pack_forget()
        for label, entry in self.sequence_entries:
            label.pack_forget()
            entry.pack_forget()
        new_servo_count = int(self.servo_count_combobox.get())
        # Ocultar o mostrar las entradas según el valor seleccionado
        for i in range(new_servo_count):
            if i < len(self.sequence_entries):
                label, entry = self.sequence_entries[i]
                label.pack()
                entry.pack()
            else:
                self.create_servo_sequence_entry(i + 1)
