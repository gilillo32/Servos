import csv
import math
import os
import pathlib
import tkinter as tk
from tkinter import ttk, filedialog
import tkinter.messagebox as messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


MAIN_PATH = pathlib.Path(__file__).parent.parent.absolute()
SEQUENCE_DIR = os.path.join(MAIN_PATH, "SECUENCIAS")

class VentanaPreparar:
    def __init__(self, master):
        self.master = master
        self.titulo = "Nueva secuencia"
        self.master.title(self.titulo)
        self.frame1 = tk.Frame(self.master)
        self.frame2 = tk.Frame(self.master)
        self.frame3 = tk.Frame(self.master)
        self.sim_frame = tk.Frame(self.master)
        self.tabla = ttk.Treeview(master, columns=("Servo 1", "Servo 2", "Tiempo de espera (s)",
                                                   "Tiempo acumulado (s)"), selectmode="browse", )
        self.tabla.heading("#0", text="Step", anchor=tk.CENTER)
        self.tabla.heading("Servo 1", text="Movimiento Servo 1")
        self.tabla.heading("Servo 2", text="Movimiento Servo 2")
        self.tabla.heading("Tiempo de espera (s)", text="Tiempo de espera (s)")
        self.tabla.heading("Tiempo acumulado (s)", text="Tiempo acumulado (s)")

        # Style
        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, 10, "bold"))
        style.configure("Treeview",
                        rowheight=20,
                        font=(None, 10),
                        )
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Centrar la columna Step
        self.tabla.column("#0", anchor=tk.CENTER)
        for col in ("Servo 1", "Servo 2", "Tiempo de espera (s)", "Tiempo acumulado (s)"):
            self.tabla.column(col, anchor=tk.CENTER)

        self.texto_acumulado = tk.StringVar(value="Tiempo acumulado: 0")
        lbl_acumulado = tk.Label(master, textvariable=self.texto_acumulado)
        lbl_acumulado.grid(row=1, column=0, columnspan=3)

        # BOTONES
        exportar_button = tk.Button(self.frame2, text="Exportar secuencia", command=self.exportar_secuencia)
        exportar_button.grid(row=1, column=0)
        cargar_button = tk.Button(self.frame2, text="Cargar secuencia", command=self.cargar_secuencia)
        cargar_button.grid(row=0, column=0)
        self.tabla.grid(row=0, column=0, columnspan=3, sticky='nsew')

        # Botón para agregar fila
        agregar_button = tk.Button(self.frame1, text="Agregar Fila", command=self.insertar_fila)
        agregar_button.grid(row=0, column=0)

        # Botón para eliminar fila
        eliminar_button = tk.Button(self.frame1, text="Eliminar Fila", command=self.eliminar_fila)
        eliminar_button.grid(row=1, column=0)

        # Botón para simular los servos
        simular_button = tk.Button(self.frame3, text="Simular Servos", command=self.simular_servos)
        simular_button.grid(row=0, column=0)

        self.frame1.grid(row=2, column=0)
        self.frame2.grid(row=2, column=1)
        self.frame3.grid(row=2, column=2)
        self.sim_frame.grid(row=0, column=3, rowspan=3, sticky='nsew')

        # Evento de doble clic para editar celdas
        self.tabla.bind("<Double-1>", self.on_double_click)
        self.insertar_fila()
        self.titulo = "Nueva secuencia"
        self.master.title(self.titulo)

    def insertar_fila(self):
        self.tabla.insert("", tk.END, text=str(len(self.tabla.get_children()) + 1), values=("0", "0", "0"))
        self.actualizar_tiempo_acumulado()
        self.marcar_cambios_no_guardados()

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
                writer.writerow(["Step", "Movimiento Servo 1", "Movimiento Servo 2", "Tiempo de espera (s)",
                                 "Tiempo acumulado (s)"])

                # Escribe los datos de cada fila
                for item in self.tabla.get_children():
                    writer.writerow([self.tabla.item(item)["text"]] + list(self.tabla.item(item)["values"]))
            if self.titulo.endswith("*"):
                self.titulo = self.titulo[:-1]
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
                        self.tabla.insert("", tk.END, text=row[0], values=row[1:])

                # Actualiza el tiempo acumulado y el título de la ventana
                self.actualizar_tiempo_acumulado()
                self.titulo = os.path.splitext(os.path.basename(file_path))[0]
                self.master.title(self.titulo)
        except Exception as e:
            messagebox.showerror("Error", f"Archivo no válido")
            # Restaurar el estado de la tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
            for fila in filas_guardadas:
                self.tabla.insert("", tk.END, text=fila[0], values=fila[1])
            self.actualizar_tiempo_acumulado()

    def marcar_cambios_no_guardados(self):
        if not self.titulo.endswith("*"):
            self.titulo += "*"
            self.master.title(self.titulo)

    def on_double_click(self, event):
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
            self.tabla.set(item, column, entry.get())
            self.actualizar_tiempo_acumulado()
            self.marcar_cambios_no_guardados()
            entry.destroy()

        entry.bind('<FocusOut>', save_edit)
        entry.bind('<Return>', save_edit)
        entry.focus_set()

    def simular_servos(self):
        # fig = self.plot_points((0, 0), 0, 1)
        for widget in self.sim_frame.winfo_children():
            widget.destroy()
        fig = plt.figure()
        # Read data from the table
        data = []
        for item in self.tabla.get_children():
            data.append(self.tabla.item(item)["values"])

        canvas = FigureCanvasTkAgg(fig, master=self.sim_frame)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        anim = animation.FuncAnimation(fig, animate, frames=len(data), interval=400, fargs=(data, fig,
                                                                                            self.master.title()),
                                       repeat_delay=3000)

        canvas.draw()

    def plot_points(self, point_1, angle_1, point_2, angle_2, length=1):
        '''
        point - Tuple (x, y)
        angle - Angle you want your end point at in degrees.
        length - Length of the line you want to plot.

        Will plot the line on a 10 x 10 plot.
        '''

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
            if messagebox.askyesno("Guardar cambios", "Hay cambios sin guardar. ¿Desea guardarlos antes de salir?"):
                self.exportar_secuencia()
        self.master.destroy()
        self.master.master.destroy()


def animate(i, data, fig, title):
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
    endy_1 = y_1 + (-1) * np.sin(np.radians(data[i][0]))
    endx_1 = x_1 + 1 * np.cos(np.radians(data[i][0]))
    endy_2 = y_2 + 1 * np.sin(np.radians(data[i][1]))
    endx_2 = x_2 + 1 * np.cos(np.radians(data[i][1]))
    # Set plot limits
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.plot([x_1, endx_1], [y_1, endy_1], color="red")
    ax.plot([x_2, endx_2], [y_2, endy_2], color="blue")
    return fig

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
