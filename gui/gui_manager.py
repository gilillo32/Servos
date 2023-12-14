import tkinter as tk

from gui.ventana_preparar import VentanaPreparar


class GUIManager:
    def __init__(self, master):
        self.master = master
        self.master.title("Control de Servos")
        self.abrir_ventana_preparar()

    def abrir_ventana_preparar(self):
        self.master.withdraw()
        ventana_preparar = tk.Toplevel(self.master)
        app_preparar = VentanaPreparar(ventana_preparar)
