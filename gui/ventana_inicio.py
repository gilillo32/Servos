import tkinter as tk


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
