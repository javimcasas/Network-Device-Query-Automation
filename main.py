"""
Network Device Automation Tool
Punto de entrada principal de la aplicación.
"""
import tkinter as tk
from src.gui.main_window import MainWindow


def main():
    """Función principal que inicia la aplicación."""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
