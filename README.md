
# Network Device Query Automation Tool

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

Herramienta de automatización para ejecutar comandos SSH en dispositivos de red y recopilar información de configuración de manera eficiente.

## 📋 Descripción

Esta aplicación permite automatizar la conexión SSH a múltiples dispositivos de red (routers, switches, etc.) y ejecutar comandos de consulta de configuración. Los resultados se procesan automáticamente y se generan reportes con el conteo de líneas de configuración encontradas.

### Características principales

- ✅ **Interfaz gráfica intuitiva** con Tkinter
- ✅ **Gestión de dispositivos** mediante archivo Excel
- ✅ **Conexión SSH automática** con soporte para TACACS+
- ✅ **Múltiples parámetros** por dispositivo (separados por comas)
- ✅ **Generación automática de reportes** con timestamp
- ✅ **Manejo robusto de errores** (timeout, autenticación)
- ✅ **Soporte multi-vendor** (Cisco, Arista, Juniper, HP, Huawei)

## 🚀 Instalación

### Requisitos previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Acceso SSH a los dispositivos de red

### Pasos de instalación

1. **Clonar el repositorio**

```bash
git clone https://github.com/javimcasas/Network-Device-Query-Automation
cd Network-Device-Query-Automation
```

2. **Crear entorno virtual** (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

## 📖 Uso

### 1. Iniciar la aplicación

```bash
python main.py
```

### 2. Configurar dispositivos

1. Click en **"Open Excel"** para crear/abrir el archivo de configuración
2. Completa las columnas:
   - **Name**: IP o hostname del dispositivo
   - **User**: Usuario SSH
   - **Password**: Contraseña SSH
   - **Parameter**: Parámetros a buscar (separados por comas)

**Ejemplo:**

| Name         | User     | Password | Parameter           |
| ------------ | -------- | -------- | ------------------- |
| 192.168.1.1  | admin    | secret   | interface,vlan,ospf |
| switch01.lan | netadmin | pass123  | port-channel,lacp   |
| router02.wan | admin    | secret   | bgp                 |

3. Guardar y cerrar Excel

### 3. Ejecutar automatización

1. Click en **"Run"**
2. El programa:
   - Se conecta a cada dispositivo por SSH
   - Ejecuta: `show configuration running-config | in {parameter}`
   - Cuenta las líneas de resultado
   - Genera reporte en `data/output_YYYYMMDD_HHMMSS.txt`
3. El archivo de resultados se abre automáticamente

### 4. Ejemplo de salida

```
======================================================================
                   NETWORK AUTOMATION RESULTS
======================================================================
Fecha: 2026-02-05 14:30:15
Total de comandos ejecutados: 5
======================================================================

✓ RESULTADOS EXITOSOS:
----------------------------------------------------------------------
  • Count for interface in 192.168.1.1: 24
  • Count for vlan in 192.168.1.1: 12
  • Count for ospf in 192.168.1.1: 8
  • Count for bgp in router02.wan: 15
  • Count for lacp in switch01.lan: 6

======================================================================
RESUMEN:
  • Comandos exitosos: 5
  • Comandos fallidos: 0
  • Total de líneas encontradas: 65
======================================================================
```

## 🏗️ Estructura del proyecto

```
network_automation/
├── main.py                          # Punto de entrada
├── requirements.txt                 # Dependencias
├── README.md                        # Documentación
├── LICENSE                          # Licencia MIT
├── .gitignore                       # Archivos ignorados por Git
│
├── src/
│   ├── gui/
│   │   └── main_window.py          # Interfaz gráfica
│   │
│   ├── services/
│   │   ├── excel_service.py        # Gestión de Excel
│   │   ├── device_service.py       # Lógica de dispositivos
│   │   └── ssh_service.py          # Conexiones SSH
│   │
│   ├── models/
│   │   ├── device.py               # Modelo Device
│   │   └── command_result.py       # Modelo CommandResult
│   │
│   └── config/
│       └── constants.py            # Constantes globales
│
└── data/                            # Archivos generados
    ├── Device_Data.xlsx            # Configuración de dispositivos
    └── output_*.txt                # Reportes generados
```

## ⚙️ Configuración avanzada

### Cambiar tipo de dispositivo

Por defecto se usa `cisco_ios`. Para cambiar el tipo de dispositivo, edita `src/services/ssh_service.py`:

```python
def __init__(self, device_type: str = 'cisco_ios', timeout: int = 30):
```

Tipos soportados:

- `cisco_ios`, `cisco_xe`, `cisco_xr`, `cisco_nxos`, `cisco_asa`
- `arista_eos`
- `juniper_junos`
- `hp_comware`, `hp_procurve`
- `huawei`

### Ajustar timeout de conexión

```python
def __init__(self, device_type: str = 'cisco_ios', timeout: int = 30):
```

## 🔒 Seguridad

- ⚠️ **No subas el archivo Excel con contraseñas** a repositorios públicos
- ⚠️ El archivo `Device_Data.xlsx` está excluido en `.gitignore`
- ✅ Considera usar un gestor de credenciales para entornos de producción
- ✅ Las contraseñas nunca se imprimen en consola (se muestran como `*****`)

## 🐛 Troubleshooting

### Error de autenticación

- Verifica usuario y contraseña en el Excel
- Confirma que el usuario tiene permisos SSH en el dispositivo

### Timeout de conexión

- Verifica conectividad de red: `ping <dispositivo>`
- Asegúrate de que SSH está habilitado en el dispositivo
- Aumenta el timeout en `ssh_service.py`

### Error "Excel no encontrado"

- Click en "Open Excel" para crear el archivo
- Verifica que el archivo existe en `data/Device_Data.xlsx`

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👤 Autor

**Javier Martínez Casas**

- GitHub: [@javimcasas](https://github.com/javimcasas)

## 🙏 Agradecimientos

- [Netmiko](https://github.com/ktbyers/netmiko) - Librería SSH para dispositivos de red
- [openpyxl](https://openpyxl.readthedocs.io/) - Gestión de archivos Excel
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - Framework GUI

---

⭐ Si este proyecto te ha sido útil, considera darle una estrella en GitHub
