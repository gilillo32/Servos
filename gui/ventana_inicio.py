import tkinter as tk
from tkinter import ttk


class VentanaPrincipal:
    def __init__(self, master):
        self.master = master
        master.title("Ventana Principal")

        self.ejecutar_button = tk.Button(master, text="Ejecutar secuencia", command=self.abrir_ventana_ejecutar)
        self.ejecutar_button.pack(side=tk.TOP, pady=10)

        self.preparar_button = tk.Button(master, text="Preparar secuencia", command=self.abrir_ventana_preparar)
        self.preparar_button.pack(side=tk.TOP, pady=10)

    def abrir_ventana_ejecutar(self):
        self.master.withdraw()
        ventana_ejecutar = tk.Toplevel(self.master)
        ventana_ejecutar.protocol("WM_DELETE_WINDOW", self.master.destroy)
        app_ejecutar = VentanaEjecutar(ventana_ejecutar)

    def abrir_ventana_preparar(self):
        self.master.withdraw()
        ventana_preparar = tk.Toplevel(self.master)
        ventana_preparar.protocol("WM_DELETE_WINDOW", self.master.destroy)
        app_preparar = VentanaPreparar(ventana_preparar)


class VentanaEjecutar:
    def __init__(self, master):
        self.master = master
        master.title("Ventana Ejecutar")


class VentanaPreparar:
    def __init__(self, master):
        self.master = master
        master.title("Ventana Preparar")
        self.tabla = ttk.Treeview(master, columns=("Servo 1", "Servo 2", "Tiempo de espera (s)"),
                                  selectmode="browse", )
        self.tabla.heading("#0", text="Step", anchor=tk.CENTER)
        self.tabla.heading("Servo 1", text="Movimiento Servo 1")
        self.tabla.heading("Servo 2", text="Movimiento Servo 2")
        self.tabla.heading("Tiempo de espera (s)", text="Tiempo de espera (s)")

        # Configurar etiquetas para centrar el texto
        self.tabla.column("#0", anchor=tk.CENTER)
        for col in ("Servo 1", "Servo 2", "Tiempo de espera (s)"):
            self.tabla.column(col, anchor=tk.CENTER)

        self.tabla.pack(expand=tk.YES, fill=tk.BOTH)

        # Botón para agregar fila
        agregar_button = tk.Button(master, text="Agregar Fila", command=self.insertar_fila)
        agregar_button.pack()

        # Botón para eliminar fila
        eliminar_button = tk.Button(master, text="Eliminar Fila", command=self.eliminar_fila)
        eliminar_button.pack()

        # Evento de doble clic para editar celdas
        self.tabla.bind("<Double-1>", self.on_double_click)
        self.insertar_fila()

    def insertar_fila(self):
        self.tabla.insert("", tk.END, text=str(len(self.tabla.get_children()) + 1), values=("0", "0", "0"))

    def eliminar_fila(self):
        selected_item = self.tabla.selection()[0]  # get selected item
        self.tabla.delete(selected_item)
        # Actualizar los números de step
        for i, item in enumerate(self.tabla.get_children()):
            self.tabla.item(item, text=str(i + 1))

    def on_double_click(self, event):
        item = self.tabla.identify('item', event.x, event.y)
        column = self.tabla.identify('column', event.x, event.y)
        value = self.tabla.set(item, column)

        entry = tk.Entry(self.master)
        entry.insert(0, value)
        entry.place(x=event.x, y=event.y, anchor=tk.CENTER)

        def save_edit(event=None):
            self.tabla.set(item, column, entry.get())
            entry.destroy()

        entry.bind('<FocusOut>', save_edit)
        entry.bind('<Return>', save_edit)
        entry.focus_set()
