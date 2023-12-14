import csv
import os
import tkinter as tk
from tkinter import ttk, filedialog
import tkinter.messagebox as messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class VentanaPreparar:
    def __init__(self, master):
        self.master = master
        self.titulo = "Nueva secuencia"
        self.master.title(self.titulo)
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
        lbl_acumulado.pack(side=tk.BOTTOM)
        exportar_button = tk.Button(master, text="Exportar secuencia", command=self.exportar_secuencia)
        exportar_button.pack(side=tk.BOTTOM)
        cargar_button = tk.Button(master, text="Cargar secuencia", command=self.cargar_secuencia)
        cargar_button.pack(side=tk.BOTTOM)
        self.tabla.pack(expand=tk.YES, fill=tk.BOTH)

        # Botón para agregar fila
        agregar_button = tk.Button(master, text="Agregar Fila", command=self.insertar_fila)
        agregar_button.pack()

        # Botón para eliminar fila
        eliminar_button = tk.Button(master, text="Eliminar Fila", command=self.eliminar_fila)
        eliminar_button.pack()

        # Botón para simular los servos
        simular_button = tk.Button(master, text="Simular Servos", command=self.simular_servos)
        simular_button.pack()

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
            self.tabla.set(item, "#4", total)
            total += self.tabla.item(item)["values"][2]
        self.texto_acumulado.set(f"Tiempo total de la secuencia: {total}s")

    # Exportar secuencia en formato csv dando la opción de elegir el nombre del archivo y la ubicación
    def exportar_secuencia(self):
        # Abre el diálogo para guardar el archivo
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

        # Si el usuario selecciona un archivo
        if file_path:
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
            file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])

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
            entry.destroy()

        entry.bind('<FocusOut>', save_edit)
        entry.bind('<Return>', save_edit)
        entry.focus_set()

    def simular_servos(self):
        # Crear animación de un círculo por cada servomotor
        fig = plt.figure()
        ax = plt.axes(xlim=(-1, 1), ylim=(-1, 1))
        ax.set_aspect('equal')
        ax.set_title("Simulación de servomotores")
        ax.grid(True)
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
        # Estilos del círculo: solo perímetro dibujado, sin relleno

        servo_1_circle = plt.Circle((0, 0), 1)
        servo_2_circle = plt.Circle((0, 1), 1)
        # Crear línea de referencia para cada círculo
        servo_1_line = ax.plot([], [], color='r')[0]
        servo_2_line = ax.plot([], [], color='b')[0]
        ax.add_patch(servo_1_circle)
        ax.add_patch(servo_2_circle)
        # Abrir la simulación en otra ventana
        sim_window = tk.Toplevel(self.master)
        sim_window.title("Simulación de servomotores")
        sim_window.geometry("500x500")
        # Crear ventana en la que se mostrarán los círculos
        canvas = FigureCanvasTkAgg(fig, master=sim_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


    def on_closing(self):
        if self.master.title().endswith("*"):
            if messagebox.askyesno("Guardar cambios", "Hay cambios sin guardar. ¿Desea guardarlos antes de salir?"):
                self.exportar_secuencia()
        self.master.destroy()
        self.master.master.destroy()

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
