"""Ventana principal de la aplicación."""
import tkinter as tk
from tkinter import messagebox
from typing import Callable
import os
import platform

from ..config.constants import (
    WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT,
    BUTTON_PADDING
)
from ..services.excel_service import ExcelService
from ..services.device_service import DeviceService



class MainWindow:
    """Ventana principal de la aplicación GUI."""
    
    def __init__(self, root: tk.Tk):
        """Inicializa la ventana principal."""
        self.root = root
        self.excel_service = ExcelService()
        self.device_service = DeviceService()
        
        self._setup_window()
        self._create_widgets()
    
    def _setup_window(self) -> None:
        """Configura las propiedades de la ventana."""
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (WINDOW_WIDTH // 2)
        y = (self.root.winfo_screenheight() // 2) - (WINDOW_HEIGHT // 2)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
    
    def _create_widgets(self) -> None:
        """Crea los widgets de la interfaz."""
        # Frame principal
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(expand=True)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Network Device Automation",
            font=("Arial", 16, "bold"),
            fg="#2C3E50"
        )
        title_label.pack(pady=(0, 30))
        
        # Frame de botones
        button_frame = tk.Frame(main_frame)
        button_frame.pack()
        
        # Botón Run
        self.run_button = self._create_button(
            button_frame,
            text="▶ Run",
            command=self._on_run_click,
            bg="#27AE60",
            fg="white"
        )
        self.run_button.pack(pady=BUTTON_PADDING)
        
        # Botón Open Excel
        self.open_excel_button = self._create_button(
            button_frame,
            text="📊 Open Excel",
            command=self._on_open_excel_click,
            bg="#3498DB",
            fg="white"
        )
        self.open_excel_button.pack(pady=BUTTON_PADDING)
        
        # Botón Clear Excel
        self.clear_excel_button = self._create_button(
            button_frame,
            text="🗑 Clear Excel",
            command=self._on_clear_excel_click,
            bg="#E74C3C",
            fg="white"
        )
        self.clear_excel_button.pack(pady=BUTTON_PADDING)
    
    def _create_button(
        self,
        parent: tk.Widget,
        text: str,
        command: Callable,
        bg: str,
        fg: str
    ) -> tk.Button:
        """Crea un botón con estilo consistente y tamaño fijo."""
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            font=("Arial", 11, "bold"),
            relief=tk.RAISED,
            cursor="hand2",
            activebackground=bg,
            activeforeground=fg,
            width=20,
            height=2,
            compound='center'
        )
        button.config(padx=5, pady=5)
        return button
    
    def _on_run_click(self) -> None:
        """Maneja el click del botón Run."""
        # Verificar si existe el Excel
        if not self.excel_service.exists():
            messagebox.showwarning(
                "Excel no encontrado",
                "Es necesario primero generar el archivo Excel.\n\n"
                "Haz click en 'Open Excel' para crearlo."
            )
            return
        
        # Deshabilitar botón durante ejecución
        self.run_button.config(state='disabled', text="⏳ Ejecutando...")
        self.root.update()
        
        try:
            # Leer dispositivos del Excel
            devices = self.excel_service.read_devices()
            
            if not devices:
                messagebox.showwarning(
                    "Sin dispositivos",
                    "No hay dispositivos registrados en el Excel.\n\n"
                    "Agrega dispositivos antes de ejecutar."
                )
                return
            
            # Ejecutar automatización
            output_file = self.device_service.execute_automation(devices)
            
            # Abrir archivo de resultados
            self._open_text_file(output_file)
            
            # Mensaje de éxito
            messagebox.showinfo(
                "✓ Proceso Completado",
                f"Se procesaron {len(devices)} dispositivos correctamente.\n\n"
                f"El archivo de resultados se ha abierto automáticamente."
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al ejecutar el proceso:\n\n{str(e)}\n\n"
                f"Revisa la consola para más detalles."
            )
        
        finally:
            # Rehabilitar botón
            self.run_button.config(state='normal', text="▶ Run")
    
    def _on_open_excel_click(self) -> None:
        """Maneja el click del botón Open Excel."""
        try:
            # Si no existe, crearlo
            if not self.excel_service.exists():
                self.excel_service.create()
                messagebox.showinfo(
                    "Excel creado",
                    f"Se ha creado el archivo Excel:\n{self.excel_service.excel_path}\n\n"
                    "Se abrirá automáticamente."
                )
            
            # Abrir el Excel
            self.excel_service.open_file()
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al abrir Excel:\n{str(e)}"
            )
    
    def _on_clear_excel_click(self) -> None:
        """Maneja el click del botón Clear Excel."""
        # Confirmar acción
        response = messagebox.askyesno(
            "Confirmar eliminación",
            "¿Estás seguro de que quieres eliminar el archivo Excel?\n\n"
            "Esta acción no se puede deshacer."
        )
        
        if response:
            try:
                self.excel_service.delete()
                messagebox.showinfo(
                    "Éxito",
                    "El archivo Excel ha sido eliminado correctamente."
                )
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Error al eliminar Excel:\n{str(e)}"
                )
    
    def _open_text_file(self, file_path) -> None:
        """Abre un archivo de texto con la aplicación predeterminada."""
        try:
            system = platform.system()
            
            if system == 'Windows':
                os.startfile(file_path)
            elif system == 'Darwin':  # macOS
                os.system(f'open "{file_path}"')
            else:  # Linux
                os.system(f'xdg-open "{file_path}"')
                
        except Exception as e:
            print(f"⚠ No se pudo abrir el archivo automáticamente: {e}")
