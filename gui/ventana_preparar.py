import csv
import os
import pathlib
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog
import tkinter.messagebox as messagebox
import matplotlib.pyplot as plt
from PIL import Image, ImageTk

import servo_collection

MAIN_PATH = pathlib.Path(__file__).parent.parent.absolute()
SEQUENCE_DIR = os.path.join(MAIN_PATH, "SECUENCIAS")


class VentanaPreparar:
    def __init__(self, master):

        # CONTROL VARIABLES
        self.simulation_status_label = None
        self.simulation_status = None
        self.progress = None
        self.save_edit_called = None
        self.simulation_paused = False
        self.stop_simulation = False
        self.movement_thread = None
        self.animation_runs_cont = 0

        self.master = master
        self.titulo = "Nueva secuencia"
        self.master.title(self.titulo)
        self.frame1 = tk.Frame(self.master)
        self.frame2 = tk.Frame(self.master)
        self.frame3 = tk.Frame(self.master)
        self.frame4 = tk.Frame(self.master)
        self.frame_exit = tk.Frame(self.master)
        self.sim_frame = tk.Frame(self.master)
        self.tabla = ttk.Treeview(master, columns=("Servo 1", "Servo 2", "Tiempo de espera (ms)",
                                                   "Tiempo acumulado (ms)"), selectmode="browse", )
        self.tabla.heading("#0", text="Step", anchor=tk.CENTER)
        self.tabla.heading("Servo 1", text="Posición Servo 1", anchor=tk.CENTER)
        self.tabla.heading("Servo 2", text="Posición Servo 2", anchor=tk.CENTER)
        self.tabla.heading("Tiempo de espera (ms)", text="Tiempo de espera (ms)", anchor=tk.CENTER)
        self.tabla.heading("Tiempo acumulado (ms)", text="Tiempo acumulado (ms)", anchor=tk.CENTER)

        # Style
        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, 10, "bold"))
        style.configure("Treeview",
                        rowheight=20,
                        font=(None, 10),
                        )
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Centrar la columna Step
        self.tabla.column("#0", anchor=tk.CENTER, width=1)
        for col in ("Servo 1", "Servo 2", "Tiempo de espera (ms)", "Tiempo acumulado (ms)"):
            self.tabla.column(col, anchor=tk.CENTER, width=60)

        self.texto_acumulado = tk.StringVar(value="Tiempo acumulado: 0")
        lbl_acumulado = tk.Label(master, textvariable=self.texto_acumulado)
        lbl_acumulado.grid(row=1, column=3, columnspan=1)

        # BOTONES
        # Botón para agregar fila
        agregar_button = tk.Button(self.frame1, text="Agregar Fila", command=self.insertar_fila, width=25, height=2,
                                   anchor='center')
        agregar_button.grid(row=0, column=0)

        # Botón para eliminar fila
        eliminar_button = tk.Button(self.frame1, text="Eliminar Fila", command=self.eliminar_fila, width=25, height=2,
                                    anchor='center')
        eliminar_button.grid(row=1, column=0)

        exportar_button = tk.Button(self.frame2, text="Exportar secuencia", command=self.exportar_secuencia, width=25,
                                    height=2, anchor='center')
        exportar_button.grid(row=1, column=0)
        cargar_button = tk.Button(self.frame2, text="Cargar secuencia", command=self.cargar_secuencia, width=25,
                                  height=2, anchor='center')
        cargar_button.grid(row=0, column=0)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=self.tabla.yview)

        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.grid(row=0, column=0, columnspan=4, sticky='nsew')

        scrollbar.grid(row=0, column=4, sticky='ns')

        limits_button = tk.Button(self.frame3, text="Marcar/Ver límites", command=self.set_limits, width=25, height=2,
                                  anchor='center')
        limits_button.grid(row=0, column=0)

        # Botón para simular los servos
        simular_button = tk.Button(self.frame4, text="Ejecutar movimiento", command=self.simular_servos,
                                   width=25,
                                   height=2,
                                   anchor='center')
        simular_button.grid(row=0, column=0)

        # Botón para cerrar la aplicación
        exit_button = tk.Button(self.frame_exit, text="Cerrar aplicación",
                                command=self.on_closing, height=2,
                                anchor='center', bg='#ed6f6f', fg='white')
        exit_button.grid(row=0, column=0, sticky='ew', columnspan=4)

        # Pausar/continuar simulación
        pause_resume_button = tk.Button(self.frame4, text="Pausar/Reanudar movimiento",
                                        command=self.pause_resume_simulation, width=25, height=2, anchor='center')
        pause_resume_button.grid(row=2, column=0)

        # Servo limits tag
        self.servo_1_limits_tag = tk.StringVar()
        self.servo_2_limits_tag = tk.StringVar()

        servo_1_limits_label = tk.Label(self.frame3, textvariable=self.servo_1_limits_tag)
        servo_1_limits_label.grid(row=1, column=0)
        servo_2_limits_label = tk.Label(self.frame3, textvariable=self.servo_2_limits_tag)
        servo_2_limits_label.grid(row=2, column=0)

        self.frame1.grid(row=2, column=0)
        self.frame2.grid(row=2, column=1)
        self.frame3.grid(row=2, column=2)
        self.frame4.grid(row=2, column=3)
        self.sim_frame.grid(row=0, column=5, rowspan=3, sticky='nsew', padx=20)
        self.frame_exit.grid(row=3, column=0, columnspan=4, sticky='nsew')
        self.frame_exit.columnconfigure(0, weight=1)

        self.moving_img = Image.open(os.path.join(MAIN_PATH, "resources", "moving.png"))
        self.paused_img = Image.open(os.path.join(MAIN_PATH, "resources", "paused.png"))
        self.loading_img = Image.open(os.path.join(MAIN_PATH, "resources", "loading.png"))

        new_size = (100, 100)

        self.moving_img = self.moving_img.resize(new_size)
        self.paused_img = self.paused_img.resize(new_size)
        self.loading_img = self.loading_img.resize(new_size)

        self.moving_img = ImageTk.PhotoImage(self.moving_img)
        self.paused_img = ImageTk.PhotoImage(self.paused_img)
        self.loading_img = ImageTk.PhotoImage(self.loading_img)

        self.simulation_status_img_label = tk.Label(self.sim_frame, image=self.paused_img)
        self.simulation_status = tk.StringVar()
        self.simulation_status.set("Movimiento en pausa")
        self.simulation_status_label = tk.Label(self.sim_frame, textvariable=self.simulation_status)
        self.simulation_status_label.pack(side=tk.BOTTOM)
        self.simulation_status_label.update()

        estado_label = tk.Label(self.sim_frame, text="Estado del\n movimiento", font=("Helvetica", 12, "bold"))
        estado_label.pack(side=tk.TOP, pady=(80, 0))
        self.simulation_status_img_label.pack(side=tk.TOP)

        # Evento de doble clic para editar celdas
        self.tabla.bind("<Double-1>", self.on_double_click)
        self.insertar_fila()
        self.titulo = "Nueva secuencia"
        self.master.title(self.titulo)

        self.set_servo_limits_tag(1,
                                  servo_collection.ServoCollectionSingleton().search_servo_by_id(1).min_limit,
                                  servo_collection.ServoCollectionSingleton().search_servo_by_id(1).max_limit)
        self.set_servo_limits_tag(2,
                                  servo_collection.ServoCollectionSingleton().search_servo_by_id(2).min_limit,
                                  servo_collection.ServoCollectionSingleton().search_servo_by_id(2).max_limit)
        # Load servo limits from file
        self.load_servo_limits()

        # Check current sequence values
        if not self.table_values_valid():
            messagebox.showwarning("Advertencia", "Hay ángulos de la secuencia que están fuera de los límites "
                                                  "actuales de los servos")

    def insertar_fila(self):
        """"
        Inserts a new row in the table
        :return: None
        """
        self.tabla.insert("", tk.END, text=str(len(self.tabla.get_children()) + 1), values=("500", "500", "0"))
        self.actualizar_tiempo_acumulado()
        self.marcar_cambios_no_guardados()
        self.tabla.see(self.tabla.get_children()[-1])

    def eliminar_fila(self):
        """"
        Deletes the selected row in the table
        :return: None
        """
        selected_item = self.tabla.selection()[0]  # get selected item
        self.tabla.delete(selected_item)
        # Actualizar los números de step
        for i, item in enumerate(self.tabla.get_children()):
            self.tabla.item(item, text=str(i + 1))
        self.actualizar_tiempo_acumulado()
        self.marcar_cambios_no_guardados()

    def actualizar_tiempo_acumulado(self):
        """
        Refreshes the total time of the sequence and updates the last column of the table
        :return: None
        """
        total = 0
        for item in self.tabla.get_children():
            total += self.tabla.item(item)["values"][2]
            self.tabla.set(item, "#4", total)
        self.texto_acumulado.set(f"Tiempo total de la secuencia: {total}ms")

    # Exportar secuencia en formato csv dando la opción de elegir el nombre del archivo y la ubicación
    def exportar_secuencia(self):
        """
        Saves the sequence in a csv file. The file must be saved in the SECUENCIAS folder
        :return: None
        """
        # Abre el diálogo para guardar el archivo
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
                                                 initialdir=SEQUENCE_DIR)
        if file_path:
            if not str(file_path).__contains__("/SECUENCIAS/"):
                messagebox.showerror("Error", f"El archivo debe guardarse en la carpeta SECUENCIAS")
                return
            # Abre el archivo en modo escritura
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)

                # Escribe los encabezados de las columnas
                writer.writerow(["Step", "Movimiento Servo 1", "Movimiento Servo 2", "Tiempo de espera (ms)",
                                 "Tiempo acumulado (ms)"])

                # Escribe los datos de cada fila
                for item in self.tabla.get_children():
                    writer.writerow([self.tabla.item(item)["text"]] + list(self.tabla.item(item)["values"]))
            if self.titulo.endswith("*"):
                self.titulo = self.titulo[:-1]
            # Set title as filename
            self.titulo = os.path.splitext(os.path.basename(file_path))[0]
            self.master.title(self.titulo)

    def cargar_secuencia(self):
        """
        Loads a sequence from a csv file
        :return: None
        """
        # Check if sequence is running
        if self.movement_thread is not None and self.movement_thread.is_alive():
            # Show error message
            messagebox.showerror("Error", "Ya hay una secuencia en ejecución, páusela antes de cargar"
                                          " otra secuencia")
            return
        # Guardar el estado actual de la tabla
        filas_guardadas = [(self.tabla.item(item)["text"], self.tabla.item(item)["values"]) for item in
                           self.tabla.get_children()]
        try:
            # Abre el diálogo para seleccionar el archivo
            file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")], initialdir=SEQUENCE_DIR)

            # Si el usuario selecciona un archivo
            if file_path:
                # Borra todas las filas existentes en la tabla
                for item in self.tabla.get_children():
                    self.tabla.delete(item)
                # Abre el archivo en modo lectura
                with open(file_path, 'r') as file:
                    reader = csv.reader(file)

                    # Ignora la primera fila (encabezados de las columnas)
                    next(reader)

                    # Por cada fila en el archivo, inserta una nueva fila en la tabla
                    for row in reader:
                        servo1_angle = int(row[1])
                        servo2_angle = int(row[2])

                        # Obtén los servos de la colección de servos
                        servo1 = servo_collection.ServoCollectionSingleton().search_servo_by_id(1)
                        servo2 = servo_collection.ServoCollectionSingleton().search_servo_by_id(2)

                        # Verifica que los ángulos estén dentro de los límites de los servos
                        if not (servo1.min_limit <= servo1_angle <= servo1.max_limit or
                                servo2.min_limit <= servo2_angle <= servo2.max_limit):
                            raise ValueError
                        self.tabla.insert("", tk.END, text=row[0], values=row[1:])

                # Actualiza el tiempo acumulado y el título de la ventana
                self.actualizar_tiempo_acumulado()
                self.titulo = os.path.splitext(os.path.basename(file_path))[0]
                self.master.title(self.titulo)
        except ValueError:
            # Restaurar el estado de la tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
            for fila in filas_guardadas:
                self.tabla.insert("", tk.END, text=fila[0], values=fila[1])
            self.actualizar_tiempo_acumulado()
            messagebox.showerror("Error", f"El archivo contiene ángulos fuera de los límites de los servos")
        except Exception as e:
            # Restaurar el estado de la tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
            for fila in filas_guardadas:
                self.tabla.insert("", tk.END, text=fila[0], values=fila[1])
            self.actualizar_tiempo_acumulado()
            messagebox.showerror("Error", f"Archivo no válido")

    def marcar_cambios_no_guardados(self):
        """
        Marks the window title with an asterisk to indicate that there are unsaved changes
        :return: None
        """
        if not self.titulo.endswith("*"):
            self.titulo += "*"
            self.master.title(self.titulo)

    def pause_resume_simulation(self):
        """
        Pauses or resumes the movement of the servos
        :return: None
        """
        self.simulation_paused = not self.simulation_paused
        if self.simulation_status is None:
            self.simulation_status = tk.StringVar()
            self.simulation_status.set("Movimiento en pausa" if self.simulation_paused else "Movimiento en ejecución")
            self.simulation_status_label = tk.Label(self.sim_frame, textvariable=self.simulation_status)
            self.simulation_status_label.pack(side=tk.BOTTOM)
        else:
            self.simulation_status.set("Movimiento en pausa" if self.simulation_paused else "Movimiento en ejecución")
            self.simulation_status_label.update()
        # Clear table selection
        if self.movement_thread.is_alive():
            self.stop_simulation = True
            print("\n[INFO] Stopping movement. . .\n")
            self.simulation_status.set("Pausando movimiento. . . Espere por favor")
            self.simulation_status_label.update()
            self.simulation_status_img_label.configure(image=self.loading_img)
        else:
            self.stop_simulation = False
            self.movement_thread = threading.Thread(target=self.start_simulation, daemon=True)
            self.movement_thread.start()
        self.tabla.selection_remove(self.tabla.selection())

    def on_double_click(self, event):
        """
        Event handler for double click event on table cells. Opens an entry to edit the cell value
        :param event: Event information (X and Y coordinates)
        :return: None
        """
        self.save_edit_called = False
        item = self.tabla.identify('item', event.x, event.y)
        column = self.tabla.identify('column', event.x, event.y)

        if column not in ("#1", "#2", "#3"):
            return
        value = self.tabla.set(item, column)

        entry = tk.Entry(self.master)
        entry.insert(0, value)
        entry.select_range(0, tk.END)
        entry.place(x=event.x, y=event.y, anchor=tk.CENTER)

        def save_edit(event=None):
            """
            Event handler for saving the edited cell value
            :param event: Not used
            :return: None
            """
            if self.save_edit_called:
                return
            self.save_edit_called = True
            # Get servo id by column
            servo_id = int(column[1:])
            servo = servo_collection.ServoCollectionSingleton().search_servo_by_id(servo_id)
            if column in ("#1", "#2"):
                if servo is None:
                    messagebox.showerror("Error", f"No se encontró el servo {servo_id}")
                    return
                try:
                    angle = int(entry.get())
                    if angle < servo.min_limit or angle > servo.max_limit:
                        raise ValueError
                except ValueError:
                    if servo.min_limit == -1 and servo.max_limit == -1:
                        messagebox.showerror("Error", f"No se han establecido los límites para el servomotor")
                    else:
                        messagebox.showerror("Error",
                                             f"El ángulo debe estar entre {servo.min_limit} y {servo.max_limit}")
                    # Destroy entry
                    entry.destroy()
                    return
            else:
                try:
                    if int(entry.get()) < 0:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Error", "Debe ingresar un valor numérico positivo y entero")
                    entry.destroy()
                    return
            self.tabla.set(item, column, entry.get())
            self.actualizar_tiempo_acumulado()
            self.marcar_cambios_no_guardados()
            entry.destroy()

        entry.bind('<FocusOut>', save_edit)
        entry.bind('<Return>', save_edit)
        entry.focus_set()

    def set_limits(self):
        """
        Opens a window to set the limits of the servos
        :return: None
        """
        def test_limit(which_limit):
            """
            Tests the limits of the selected servo. Moves the servo to the limit
            :param which_limit: Min or max limit
            :return: None
            """
            servo_id = int(servo_combobox.get().split(" ")[1])
            curr_servo = servo_collection.ServoCollectionSingleton().search_servo_by_id(servo_id)
            if curr_servo is None:
                messagebox.showerror("Error", f"No se encontró el servo {servo_id}")
                return

            if min_limit_entry.get() == "" or max_limit_entry.get() == "":
                messagebox.showerror("Error", f"Debe ingresar un valor para el límite")
                return
            try:
                min_limit = int(min_limit_entry.get())
                max_limit = int(max_limit_entry.get())
                limit = None
                if which_limit == "min":
                    limit = min_limit
                elif which_limit == "max":
                    limit = max_limit
                curr_servo.move(limit)
                # Request focus on limits_window
                limits_window.after(100, lambda: limits_window.focus_force())

            except ValueError:
                messagebox.showerror("Error", f"Asegúrese de introducir un valor válido para el límite")

            # Pause simulation
            self.simulation_paused = True

        # Open window to set servo motor limits
        limits_window = tk.Toplevel(self.master)
        limits_window.title("Límites de los servos")
        limits_window.geometry("600x300")
        # Desplegable con la lista de servos
        servo_id_list = []
        servo_list = servo_collection.ServoCollectionSingleton().get_servos()
        for servo in servo_list:
            servo_id_list.append("Servo " + str(servo.id))
        servo_combobox = ttk.Combobox(limits_window, values=servo_id_list)
        servo_combobox.grid(row=0, column=0, columnspan=2, pady=20, padx=20)
        if servo_id_list:
            servo_combobox.set(servo_id_list[0])
        min_limit_label = tk.Label(limits_window, text="Límite mínimo")
        min_limit_label.grid(row=1, column=0, padx=20)
        max_limit_label = tk.Label(limits_window, text="Límite máximo")
        max_limit_label.grid(row=1, column=1, padx=20)
        min_limit_entry = tk.Spinbox(limits_window, from_=500, to=2100, increment=30, command=lambda: test_limit("min"))
        min_limit_entry.grid(row=2, column=0, pady=20, padx=20)
        max_limit_entry = tk.Spinbox(limits_window, from_=500, to=2100, increment=30, command=lambda: test_limit("max"))
        max_limit_entry.grid(row=2, column=1, pady=20, padx=20)
        # Botón para guardar los límites
        save_button = tk.Button(limits_window, text="Guardar", command=lambda: self.save_limits(servo_combobox,
                                                                                                min_limit_entry,
                                                                                                max_limit_entry))
        save_button.grid(row=3, column=0, columnspan=2, padx=20)

        # Botón para probar los límites
        min_limit_button = tk.Button(limits_window, text="Probar límite mínimo", command=lambda: test_limit("min"))
        min_limit_button.grid(row=4, column=0, pady=20, padx=20)
        max_limit_button = tk.Button(limits_window, text="Probar límite máximo", command=lambda: test_limit("max"))
        max_limit_button.grid(row=4, column=1, pady=20, padx=20)

        def on_servo_selected(event):
            """
            Event handler for servo selection
            :param event: None
            :return: None
            """
            current_servo_id = int(servo_combobox.get().split(" ")[1])
            current_servo = servo_collection.ServoCollectionSingleton().search_servo_by_id(current_servo_id)
            if current_servo is None:
                messagebox.showerror("Error", f"No se encontró el servo {current_servo_id}")
                return
            min_limit_entry.delete(0, tk.END)
            max_limit_entry.delete(0, tk.END)
            min_limit_entry.insert(0, current_servo.min_limit)
            max_limit_entry.insert(0, current_servo.max_limit)

        on_servo_selected(None)
        servo_combobox.bind("<<ComboboxSelected>>", on_servo_selected)

    def save_limits(self, servo_combobox, min_limit_entry, max_limit_entry):
        """
        Saves the limits of the selected servo
        :param servo_combobox: Combobox object
        :param min_limit_entry: Entry object
        :param max_limit_entry: Entry object
        :return: None
        """
        servo_id = int(servo_combobox.get().split(" ")[1])
        servo = servo_collection.ServoCollectionSingleton().search_servo_by_id(servo_id)
        if servo is None:
            messagebox.showerror("Error", f"No se encontró el servo {servo_id}")
            return
        try:
            min_limit = int(min_limit_entry.get())
            max_limit = int(max_limit_entry.get())
            if min_limit > max_limit:
                raise ValueError
            servo.min_limit = min_limit
            servo.max_limit = max_limit
            # Check current sequence values
            for item in self.tabla.get_children():
                servo_1_angle = int(self.tabla.item(item)["values"][0])
                servo_2_angle = int(self.tabla.item(item)["values"][1])
                if servo_1_angle < min_limit or servo_1_angle > max_limit or servo_2_angle < min_limit or \
                        servo_2_angle > max_limit:
                    messagebox.showwarning("Advertencia", f"Hay ángulos de la secuencia que están fuera "
                                                          f"de los" f" límites"f" actuales del servo {servo_id}")
                    break
            messagebox.showinfo("Información", f"Límites del servo {servo_id} guardados correctamente")
            self.set_servo_limits_tag(servo_id, min_limit, max_limit)
        except ValueError:
            messagebox.showerror("Error", f"El límite mínimo debe ser inferior al máximo")

    def set_servo_limits_tag(self, servo_id, min_limit, max_limit):
        """
        Sets the servo limits tag
        :param servo_id:
        :param min_limit:
        :param max_limit:
        :return: None
        """
        if servo_id == 1:
            self.servo_1_limits_tag.set(f"Límites del servo {servo_id}: {min_limit} - {max_limit}")
        elif servo_id == 2:
            self.servo_2_limits_tag.set(f"Límites del servo {servo_id}: {min_limit} - {max_limit}")

    def table_values_valid(self, servo=None):
        """
        Checks if the values in the table are valid (inside the limits of the servos)
        :param servo: Servo to check
        :return: True if valid, False otherwise
        """
        if servo is None:
            for item in self.tabla.get_children():
                servo_1_angle = int(self.tabla.item(item)["values"][0])
                servo_2_angle = int(self.tabla.item(item)["values"][1])
                if servo_1_angle < servo_collection.ServoCollectionSingleton().search_servo_by_id(1).min_limit or \
                        servo_1_angle > servo_collection.ServoCollectionSingleton().search_servo_by_id(1).max_limit or \
                        servo_2_angle < servo_collection.ServoCollectionSingleton().search_servo_by_id(2).min_limit or \
                        servo_2_angle > servo_collection.ServoCollectionSingleton().search_servo_by_id(2).max_limit:
                    return False
            return True
        else:
            for item in self.tabla.get_children():
                servo_angle = int(self.tabla.item(item)["values"][servo.id - 1])
                if servo_angle < servo.min_limit or servo_angle > servo.max_limit:
                    return False
            return True

    def simular_servos(self, p_data=None):
        """
        Starts the movement of the servos
        :param p_data: None
        :return: None
        """
        # Check table values
        if not self.table_values_valid():
            messagebox.showerror("Error", "Hay ángulos de la secuencia que están fuera de los límites "
                                          "actuales de los servos")
            return
        self.animation_runs_cont = 0
        self.stop_simulation = False
        if self.movement_thread is not None and self.movement_thread.is_alive():
            # Show error message
            messagebox.showerror("Error", "Ya hay una secuencia en ejecución, páusela antes de ejecutar"
                                          " otra secuencia")
            return
        self.movement_thread = threading.Thread(target=self.start_simulation, daemon=False)
        self.movement_thread.start()

    def close_simulation(self):
        """
        Stops the simulation of the servos
        :return: None
        """
        self.stop_simulation = True
        self.simulation_paused = True
        self.movement_thread = None
        if self.simulation_status is not None:
            self.simulation_status.set("Movimiento en pausa" if self.simulation_paused else "Movimiento en ejecución")
            self.simulation_status_label.update()
            self.simulation_status_img_label.configure(image=self.paused_img if self.simulation_paused else self.
                                                       moving_img)
        # Clear table selection
        self.tabla.selection_remove(self.tabla.selection())

    def start_simulation(self, p_data=None):
        """
        Starts the simulation of the servos
        :param p_data: Table data
        :return: None
        """
        self.simulation_paused = False
        self.stop_simulation = False
        if self.stop_simulation:
            self.close_simulation()
        fig = plt.figure(figsize=(2, 2))
        # Read data from the table
        data = []
        for item in self.tabla.get_children():
            data.append(self.tabla.item(item)["values"])
        if p_data is not None:
            data = p_data

        if self.progress is None:
            self.progress = ttk.Progressbar(self.sim_frame, orient=tk.HORIZONTAL,
                                            length=len(data), mode='determinate',
                                            maximum=len(data))
            self.progress.pack(side=tk.BOTTOM, fill=tk.X)
        if self.simulation_status is None:
            # Initialize simulation status label
            self.simulation_status = tk.StringVar()
            self.simulation_status.set("Movimiento en pausa" if self.simulation_paused else "Movimiento en ejecución")
            self.simulation_status_label = tk.Label(self.sim_frame, textvariable=self.simulation_status)
            self.simulation_status_label.pack(side=tk.BOTTOM)
            self.simulation_status_img_label.configure(image=self.paused_img if self.simulation_paused else self.
                                                       moving_img)
        else:
            self.simulation_status.set("Movimiento en ejecución")
            self.simulation_status_label.update()
            self.simulation_status_img_label.configure(image=self.paused_img if self.simulation_paused else self.
                                                       moving_img)
        parsed_data = data
        # TODO progress is now a common variable, it should not be passed as an argument
        animate(0, parsed_data, None, self.master.title(), self.tabla, self.progress, self)

    def on_closing(self):
        # Check if sequence is executing
        if self.movement_thread is not None and self.movement_thread.is_alive():
            # Show error message
            messagebox.showerror("Error", "No se puede cerrar la aplicación mientras haya una secuencia "
                                          "en ejecución")
            return
        self.export_servo_limits()
        if self.master.title().endswith("*"):
            if messagebox.askyesno("Guardar cambios",
                                   "Hay cambios sin guardar. ¿Desea guardarlos antes de salir?"):
                self.exportar_secuencia()
        self.master.destroy()
        self.master.master.destroy()
        exit()

    def load_servo_limits(self):
        """
        Loads servo limits from file, if file does not exist, default limits are loaded (500 - 2100)
        :return: None
        """
        print("[INFO] Loading servo limits. . .")
        try:
            with open(os.path.join(MAIN_PATH, "servo_limits"), "r") as file:
                lines = file.readlines()
                for line in lines:
                    servo_id, min_limit, max_limit = line.split(",")
                    servo_id = int(servo_id)
                    min_limit = int(min_limit)
                    max_limit = int(max_limit)
                    servo = servo_collection.ServoCollectionSingleton().search_servo_by_id(servo_id)
                    if servo is None:
                        messagebox.showerror("Error", f"No se encontró el servo {servo_id}.")
                        return
                    servo.min_limit = min_limit
                    servo.max_limit = max_limit
                    self.set_servo_limits_tag(servo_id, min_limit, max_limit)
        except FileNotFoundError:
            messagebox.showwarning("Advertencia", "No se encontró el archivo servo_limits. Se cargarán "
                                                  "los límites por defecto (500 - 2100)")
        except ValueError:
            messagebox.showerror("Error", "El archivo servo_limits está corrupto. Se cargarán los "
                                          "límites por defecto (500 - 2100)")

    def export_servo_limits(self):
        """
        Saves servo limits to file
        :return: None
        """
        print("[INFO] Exporting servo limits. . .")
        with open(os.path.join(MAIN_PATH, "servo_limits"), "w") as file:
            for servo in servo_collection.ServoCollectionSingleton().get_servos():
                file.write(f"{servo.id},{servo.min_limit},{servo.max_limit}\n")


def animate(i, data, fig, title, table, progress, ventana_preparar):
    """"
    Animates the movement of the servos
    :param i: Current step
    :param data: Sequence data
    :param fig: Figure to plot
    :param title: Title of the window
    :param table: Table widget
    :param progress: Progress bar
    :param ventana_preparar: VentanaPreparar instance
    :return: None
    """
    while True:
        # Check if program is creating more than 2 threads
        if ventana_preparar.stop_simulation:
            print("\n[INFO] Movement stopped\n")
            ventana_preparar.simulation_status.set("Movimiento en pausa")
            ventana_preparar.simulation_status_label.update()
            ventana_preparar.simulation_status_img_label.configure(image=ventana_preparar.
                                                                   paused_img if ventana_preparar.
                                                                   simulation_paused else ventana_preparar.moving_img)
            return
        if i != 0 and ventana_preparar.animation_runs_cont != 0:
            time.sleep(data[i - 1][2] / 1000)
        elif i == 0 and ventana_preparar.animation_runs_cont != 0:
            time.sleep(data[-1][2] / 1000)

        if i == 0:
            ventana_preparar.animation_runs_cont += 1
        # Move servos
        servo_1 = servo_collection.ServoCollectionSingleton().search_servo_by_id(1)
        servo_2 = servo_collection.ServoCollectionSingleton().search_servo_by_id(2)
        servo_1.move(data[i][0])
        servo_2.move(data[i][1])

        # Visualize in table
        table.selection_clear()
        table.selection_set(table.get_children()[i])
        progress['value'] = i + 1
        i += 1

        table.see(table.get_children()[i - 1])
        if i == len(data):
            i = 0


def pwm_to_degrees(pwm):
    """
    Converts a PWM value to degrees assuming 500 as 0 degrees and 2100 as 180 degrees
    :param pwm: The PWM value to convert. It must be in the range 500 - 2100
    :return: Corresponding angle in degrees
    """
    return (pwm - 500) * 180 / (2100 - 500)

#   Backup execute_sequence
#     def execute_sequence(self):
#         servo_count = int(self.servo_count_var.get())
#
#         for i in range(servo_count):
#             sequence = self.sequence_entries[i].get()
#             sequence = list(map(int, sequence.split(",")))
#             servo = servo_collection.ServoCollectionSingleton().search_servo_by_id(i)
#             servo.sequence = sequence
#         waiting_sequence = list(map(int, self.waiting_sequence_entry.get().split(",")))
#         servo_collection.ServoCollectionSingleton().set_waiting_sequence(waiting_sequence)
#         servo_collection.ServoCollectionSingleton().execute_sequence()
