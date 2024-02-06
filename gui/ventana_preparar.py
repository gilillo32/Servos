import csv
import math
import os
import gc
import pathlib
import tkinter as tk
from tkinter import ttk, filedialog
import tkinter.messagebox as messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import servo_collection

MAIN_PATH = pathlib.Path(__file__).parent.parent.absolute()
SEQUENCE_DIR = os.path.join(MAIN_PATH, "SECUENCIAS")


class VentanaPreparar:
    def __init__(self, master):
        self.simulation_status_label = None
        self.simulation_status = None
        self.save_edit_called = None
        self.simulation_paused = False
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
        simular_button = tk.Button(self.frame4, text="Simular/Ejecutar movimiento", command=self.simular_servos, width=25,
                                   height=2,
                                   anchor='center')
        simular_button.grid(row=0, column=0)

        # Botón para cerrar la aplicación
        exit_button = tk.Button(self.frame_exit, text="Cerrar aplicación",
                                command=self.on_closing, height=2,
                                anchor='center', bg='#ed6f6f', fg='white')
        exit_button.grid(row=0, column=0, sticky='ew', columnspan=4)

        # Pausar/continuar simulación
        pause_resume_button = tk.Button(self.frame4, text="Pausar/Reanudar simulación",
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
        self.sim_frame.grid(row=0, column=5, rowspan=3, sticky='nsew')
        self.frame_exit.grid(row=3, column=0, columnspan=4, sticky='nsew')
        self.frame_exit.columnconfigure(0, weight=1)

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
        self.simular_servos()

    def insertar_fila(self):
        self.tabla.insert("", tk.END, text=str(len(self.tabla.get_children()) + 1), values=("500", "500", "0"))
        self.actualizar_tiempo_acumulado()
        self.marcar_cambios_no_guardados()
        self.tabla.see(self.tabla.get_children()[-1])

    def eliminar_fila(self):
        selected_item = self.tabla.selection()[0]  # get selected item
        self.tabla.delete(selected_item)
        # Actualizar los números de step
        for i, item in enumerate(self.tabla.get_children()):
            self.tabla.item(item, text=str(i + 1))
        self.actualizar_tiempo_acumulado()
        self.marcar_cambios_no_guardados()

    def actualizar_tiempo_acumulado(self):
        total = 0
        for item in self.tabla.get_children():
            total += self.tabla.item(item)["values"][2]
            self.tabla.set(item, "#4", total)
        self.texto_acumulado.set(f"Tiempo total de la secuencia: {total}s")

    # Exportar secuencia en formato csv dando la opción de elegir el nombre del archivo y la ubicación
    def exportar_secuencia(self):
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
        if not self.titulo.endswith("*"):
            self.titulo += "*"
            self.master.title(self.titulo)

    def pause_resume_simulation(self):
        self.simulation_paused = not self.simulation_paused
        self.simulation_status.set("Simulación en pausa" if self.simulation_paused else "Simulación en ejecución")

    def on_double_click(self, event):
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
        def test_limit(which_limit):
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
                if servo_id == 1:
                    self.simular_servos(p_data=[[limit, 500, 0, 0]])
                elif servo_id == 2:
                    self.simular_servos(p_data=[[0, limit, 500, 0]])
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
        limits_window.geometry("270x300")
        # Desplegable con la lista de servos
        servo_id_list = []
        servo_list = servo_collection.ServoCollectionSingleton().get_servos()
        for servo in servo_list:
            servo_id_list.append("Servo " + str(servo.id))
        servo_combobox = ttk.Combobox(limits_window, values=servo_id_list)
        servo_combobox.grid(row=0, column=0, columnspan=2, pady=20)
        if servo_id_list:
            servo_combobox.set(servo_id_list[0])
        min_limit_label = tk.Label(limits_window, text="Límite mínimo")
        min_limit_label.grid(row=1, column=0)
        max_limit_label = tk.Label(limits_window, text="Límite máximo")
        max_limit_label.grid(row=1, column=1)
        min_limit_entry = tk.Spinbox(limits_window, from_=500, to=2100, increment=30, command=lambda: test_limit("min"))
        min_limit_entry.grid(row=2, column=0, pady=20)
        max_limit_entry = tk.Spinbox(limits_window, from_=500, to=2100, increment=30, command=lambda: test_limit("max"))
        max_limit_entry.grid(row=2, column=1, pady=20)
        # Botón para guardar los límites
        save_button = tk.Button(limits_window, text="Guardar", command=lambda: self.save_limits(servo_combobox,
                                                                                                min_limit_entry,
                                                                                                max_limit_entry))
        save_button.grid(row=3, column=0, columnspan=2)

        # Botón para probar los límites
        min_limit_button = tk.Button(limits_window, text="Probar límite mínimo", command=lambda: test_limit("min"))
        min_limit_button.grid(row=4, column=0, pady=20)
        max_limit_button = tk.Button(limits_window, text="Probar límite máximo", command=lambda: test_limit("max"))
        max_limit_button.grid(row=4, column=1, pady=20)

        def on_servo_selected(event):
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
            messagebox.showinfo("Información", f"Límites del servo {servo_id} guardados correctamente")
            self.set_servo_limits_tag(servo_id, min_limit, max_limit)
        except ValueError:
            messagebox.showerror("Error", f"El límite mínimo debe ser inferior al máximo")

    def set_servo_limits_tag(self, servo_id, min_limit, max_limit):
        if servo_id == 1:
            self.servo_1_limits_tag.set(f"Límites del servo {servo_id}: {min_limit} - {max_limit}")
        elif servo_id == 2:
            self.servo_2_limits_tag.set(f"Límites del servo {servo_id}: {min_limit} - {max_limit}")

    def simular_servos(self, p_data=None):
        self.simulation_paused = False
        for widget in self.sim_frame.winfo_children():
            widget.destroy()
        fig = plt.figure(figsize=(2, 2))
        # Read data from the table
        data = []
        for item in self.tabla.get_children():
            data.append(self.tabla.item(item)["values"])
        if p_data is not None:
            data = p_data
        canvas = FigureCanvasTkAgg(fig, master=self.sim_frame)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        progress = ttk.Progressbar(self.sim_frame, orient=tk.HORIZONTAL,
                                   length=len((self.parse_data_for_animation(data))), mode='determinate',
                                   maximum=len(self.parse_data_for_animation(data)))
        progress.pack(side=tk.BOTTOM, fill=tk.X)
        self.simulation_status = tk.StringVar()
        self.simulation_status.set("Simulación en pausa" if self.simulation_paused else "Simulación en ejecución")
        self.simulation_status_label = tk.Label(self.sim_frame, textvariable=self.simulation_status)
        self.simulation_status_label.pack(side=tk.BOTTOM)
        parsed_data = self.parse_data_for_animation(data)
        print(data)
        print(parsed_data)
        anim = animation.FuncAnimation(fig,
                                       animate,
                                       frames=len(parsed_data),
                                       interval=100,
                                       fargs=(parsed_data, fig, self.master.title(), self.tabla, progress, self),
                                       )

        canvas.draw()

    def plot_points(self, point_1, angle_1, point_2, angle_2, length=1):
        """
        point - Tuple (x, y)
        angle - Angle you want your end point at in degrees.
        length - Length of the line you want to plot.

        Will plot the line on a 10 x 10 plot.
        """

        # unpack the first point
        x_1, y_1 = point_1
        x_2, y_2 = point_2

        # find the end point
        endy_1 = y_1 + length * math.sin(math.degrees(angle_1))
        endx_1 = x_1 + length * math.cos(math.degrees(angle_1))

        endy_2 = y_2 + length * math.sin(math.degrees(angle_2))
        endx_2 = x_2 + length * math.cos(math.degrees(angle_2))

        # plot the points
        fig = plt.figure()
        ax = plt.axes(xlim=(-1, 1), ylim=(-1, 1))
        ax.set_aspect('equal')
        # Set window title same as window title
        ax.set_title(self.master.title())
        ax.grid(False)
        ax.set_xticks(np.arange(-1, 1.1, 0.1))
        ax.set_yticks(np.arange(-1, 1.1, 0.1))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_facecolor("black")
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax = plt.subplot(111)
        ax.plot([x_1, endx_1], [y_1, endy_1])

        return fig

    def on_closing(self):
        if self.master.title().endswith("*"):
            if messagebox.askyesno("Guardar cambios",
                                   "Hay cambios sin guardar. ¿Desea guardarlos antes de salir?"):
                self.exportar_secuencia()
        self.master.destroy()
        self.master.master.destroy()
        exit()


    def parse_data_for_animation(self, data):
        """
        Prepares data for animation by simulating wait times between each step.
        This function takes a list of data, where each element is a list containing the positions of two servos and a
        wait time. The wait time is specified in the third column of the data and is in milliseconds.
        To simulate the wait time, this function duplicates each row in the data. The number of times a row is
        duplicated is calculated by dividing the wait time by 100, as each frame in the animation is executed every
        100 ms.
        For example, if a wait time of 3 seconds is desired, the same frame would need to be repeated 30 times.
        The function returns a new list of data where each row has been duplicated the necessary number of times to
         simulate the corresponding wait time.

        Parameters:
        data (list): A list of lists. Each sublist contains two servo positions and a wait time.

        Returns:
        parsed_data (list): A new list of data prepared for animation.
        """
        parsed_data = []
        for i, step in enumerate(data):
            # Calcula cuántas veces se debe duplicar la fila
            num_repeats = round(step[2] / 100)
            # Duplica la fila num_repeats veces
            for _ in range(num_repeats + 1):
                parsed_data.append([step[0], step[1], step[2], i])
        return parsed_data


def animate(i, data, fig, title, table, progress, ventana_preparar):
    if ventana_preparar.simulation_paused:
        gc.collect()
        return fig
    if i == len(data):
        plt.close(fig)
        gc.collect()
        return fig

    # Create animation
    ax = plt.subplot(111)
    ax.clear()
    ax.set_aspect('equal')
    ax.set_title(title)
    ax.grid(False)
    ax.set_xticks(np.arange(-1, 1.1, 0.1))
    ax.set_yticks(np.arange(-1, 1.1, 0.1))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_facecolor("black")
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white')
    ax.spines['right'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax = plt.subplot(111)
    # unpack the first point
    x_1 = 0
    y_1 = 0
    x_2 = 0
    y_2 = -1

    # find the end point
    endy_1 = y_1 + 1 * np.sin(np.radians(pwm_to_degrees(data[i][0])))
    endx_1 = x_1 + 1 * np.cos(np.radians(pwm_to_degrees(data[i][0])))
    endy_2 = y_2 + 1 * np.sin(np.radians(pwm_to_degrees(data[i][1])))
    endx_2 = x_2 + 1 * np.cos(np.radians(pwm_to_degrees(data[i][1])))
    # Set plot limits
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.plot([x_1, endx_1], [y_1, endy_1], color="red")
    ax.plot([x_2, endx_2], [y_2, endy_2], color="blue")

    # Visualize in table
    table.selection_clear()
    table.selection_set(table.get_children()[data[i][3]])
    progress['value'] = i + 1
    i += 1

    servo_1 = servo_collection.ServoCollectionSingleton().search_servo_by_id(1)
    servo_2 = servo_collection.ServoCollectionSingleton().search_servo_by_id(2)
    servo_1.move(data[i - 1][0])
    servo_2.move(data[i - 1][1])
    table.see(table.get_children()[data[i - 1][3]])

    return fig


def pwm_to_degrees(pwm):
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
