"""Constantes de configuración de la aplicación."""
from pathlib import Path

# Rutas
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EXCEL_FILENAME = "Device_Data.xlsx"
EXCEL_PATH = DATA_DIR / EXCEL_FILENAME

# Configuración Excel
EXCEL_COLUMNS = ["Name", "User", "Password", "Parameter"]

# Configuración GUI
WINDOW_TITLE = "Network Device Automation"
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 400
BUTTON_WIDTH = 20
BUTTON_HEIGHT = 2
BUTTON_PADDING = 10
