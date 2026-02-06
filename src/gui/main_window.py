"""Ventana principal de la aplicación."""
import tkinter as tk
from tkinter import messagebox
from typing import Callable
import os
import platform

from ..config.constants import (
    WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT,
    BUTTON_PADDING, JUMP_HOST_ENABLED, JUMP_HOST,
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
        
        # Variables para jump host (las leeremos al pulsar Run)
        self.jump_host_var = tk.StringVar(value=JUMP_HOST)
        self.jump_user_var = tk.StringVar()
        self.jump_pass_var = tk.StringVar()
        
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
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Network Device Automation",
            font=("Arial", 16, "bold"),
            fg="#2C3E50",
        )
        title_label.pack(pady=(0, 10))
        
        # Frame de configuración de jump host
        jump_frame = tk.LabelFrame(
            main_frame, text="Jump host (bastion)", padx=10, pady=10
        )
        jump_frame.pack(fill="x", pady=(0, 15))
        
        # Host
        tk.Label(jump_frame, text="Host/IP:", font=("Arial", 10)).grid(
            row=0, column=0, sticky="w"
        )
        tk.Entry(
            jump_frame, textvariable=self.jump_host_var, width=25
        ).grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        # Usuario
        tk.Label(jump_frame, text="User:", font=("Arial", 10)).grid(
            row=1, column=0, sticky="w"
        )
        tk.Entry(
            jump_frame, textvariable=self.jump_user_var, width=25
        ).grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        # Password
        tk.Label(jump_frame, text="Password:", font=("Arial", 10)).grid(
            row=2, column=0, sticky="w"
        )
        tk.Entry(
            jump_frame, textvariable=self.jump_pass_var, width=25, show="*"
        ).grid(row=2, column=1, padx=5, pady=2, sticky="w")
        
        # Nota
        tk.Label(
            jump_frame,
            text="(Si dejas user/pass vacíos se intentará conectar directamente al equipo)",
            font=("Arial", 8),
            fg="#7F8C8D",
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(4, 0))
        
        # Frame de botones
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # Botón Run
        self.run_button = self._create_button(
            button_frame,
            text="▶ Run",
            command=self._on_run_click,
            bg="#27AE60",
            fg="white",
        )
        self.run_button.pack(pady=BUTTON_PADDING)
        
        # Botón Open Excel
        self.open_excel_button = self._create_button(
            button_frame,
            text="📊 Open Excel",
            command=self._on_open_excel_click,
            bg="#3498DB",
            fg="white",
        )
        self.open_excel_button.pack(pady=BUTTON_PADDING)
        
        # Botón Clear Excel
        self.clear_excel_button = self._create_button(
            button_frame,
            text="🗑 Clear Excel",
            command=self._on_clear_excel_click,
            bg="#E74C3C",
            fg="white",
        )
        self.clear_excel_button.pack(pady=BUTTON_PADDING)
    
    def _create_button(
        self,
        parent: tk.Widget,
        text: str,
        command: Callable,
        bg: str,
        fg: str,
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
            compound="center",
        )
        button.config(padx=5, pady=5)
        return button
    
    def _on_run_click(self) -> None:
        """Maneja el click del botón Run."""
        if not self.excel_service.exists():
            messagebox.showwarning(
                "Excel no encontrado",
                "Es necesario primero generar el archivo Excel.\n\n"
                "Haz click en 'Open Excel' para crearlo.",
            )
            return
        
        # Recoger config de jump host
        jump_host = self.jump_host_var.get().strip()
        jump_user = self.jump_user_var.get().strip()
        jump_pass = self.jump_pass_var.get().strip()
        
        # Deshabilitar botón durante ejecución
        self.run_button.config(state="disabled", text="⏳ Ejecutando...")
        self.root.update()
        
        try:
            devices = self.excel_service.read_devices()
            
            if not devices:
                messagebox.showwarning(
                    "Sin dispositivos",
                    "No hay dispositivos registrados en el Excel.\n\n"
                    "Agrega dispositivos antes de ejecutar.",
                )
                return
            
            # Ejecutar automatización (pasando datos de jump host)
            output_file = self.device_service.execute_automation(
                devices,
                jump_host=jump_host if jump_host else None,
                jump_user=jump_user if jump_user else None,
                jump_pass=jump_pass if jump_pass else None,
            )
            
            self._open_text_file(output_file)
            
            messagebox.showinfo(
                "✓ Proceso Completado",
                f"Se procesaron {len(devices)} dispositivos correctamente.\n\n"
                f"El archivo de resultados se ha abierto automáticamente.",
            )
        
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al ejecutar el proceso:\n\n{str(e)}\n\n"
                f"Revisa la consola para más detalles.",
            )
        
        finally:
            self.run_button.config(state="normal", text="▶ Run")
    
    def _on_open_excel_click(self) -> None:
        """Maneja el click del botón Open Excel."""
        try:
            if not self.excel_service.exists():
                self.excel_service.create()
                messagebox.showinfo(
                    "Excel creado",
                    f"Se ha creado el archivo Excel:\n{self.excel_service.excel_path}\n\n"
                    "Se abrirá automáticamente.",
                )
            
            self.excel_service.open_file()
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir Excel:\n{str(e)}")
    
    def _on_clear_excel_click(self) -> None:
        """Maneja el click del botón Clear Excel."""
        response = messagebox.askyesno(
            "Confirmar eliminación",
            "¿Estás seguro de que quieres eliminar el archivo Excel?\n\n"
            "Esta acción no se puede deshacer.",
        )
        
        if response:
            try:
                self.excel_service.delete()
                messagebox.showinfo(
                    "Éxito", "El archivo Excel ha sido eliminado correctamente."
                )
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar Excel:\n{str(e)}")
    
    def _open_text_file(self, file_path) -> None:
        """Abre un archivo de texto con la aplicación predeterminada."""
        try:
            system = platform.system()
            
            if system == "Windows":
                os.startfile(file_path)
            elif system == "Darwin":
                os.system(f'open "{file_path}"')
            else:
                os.system(f'xdg-open "{file_path}"')
        
        except Exception as e:
            print(f"⚠ No se pudo abrir el archivo automáticamente: {e}")
