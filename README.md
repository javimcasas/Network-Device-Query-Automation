
# Network Device Query Automation Tool

![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

Herramienta de automatización para ejecutar comandos SSH en dispositivos de red y recopilar información de configuración de manera eficiente.

## 📋 Descripción

Esta aplicación permite automatizar la conexión SSH a múltiples dispositivos de red (routers, switches, etc.) y ejecutar comandos de consulta de configuración. Los resultados se procesan automáticamente y se generan reportes con el conteo de líneas de configuración encontradas.

### Características principales

✅ Interfaz gráfica intuitiva con Tkinter
✅ Gestión de dispositivos mediante archivo Excel
✅ Conexión SSH automática con soporte para TACACS+
✅ **Soporte para conexión a través de Jump Server/Bastion Host**
✅ Múltiples parámetros por dispositivo (separados por comas)
✅ Generación automática de reportes con timestamp
✅ Manejo robusto de errores (timeout, autenticación)
✅ Soporte multi-vendor (Cisco, Arista, Juniper, HP, Huawei)

## 🚀 Instalación

### Requisitos previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Acceso SSH a los dispositivos de red
- (Opcional) Acceso SSH a servidor de salto/jump server

### Pasos de instalación

**1. Clonar el repositorio**

```bash
git clone https://github.com/javimcasas/Network-Device-Query-Automation
cd Network-Device-Query-Automation
```

**2. Crear entorno virtual (recomendado)**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

**3. Instalar dependencias**

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
2. Completa las columnas requeridas según tu escenario de conexión

#### Escenario A: Conexión directa (sin Jump Server)

Si tienes acceso directo desde tu máquina local a los dispositivos de red:

| Name         | User     | Password | Parameter           | Jump_Host | Jump_User | Jump_Password |
| ------------ | -------- | -------- | ------------------- | --------- | --------- | ------------- |
| 192.168.1.1  | admin    | secret   | interface,vlan,ospf |           |           |               |
| switch01.lan | netadmin | pass123  | port-channel,lacp   |           |           |               |
| router02.wan | admin    | secret   | bgp                 |           |           |               |

**Deja vacías las columnas Jump_Host, Jump_User y Jump_Password** para conexión directa.

#### Escenario B: Conexión a través de Jump Server

Si los dispositivos solo son accesibles a través de un servidor de salto/bastion host:

| Name              | User     | Password | Parameter      | Jump_Host        | Jump_User    | Jump_Password |
| ----------------- | -------- | -------- | -------------- | ---------------- | ------------ | ------------- |
| 10.10.10.1        | admin    | secret   | interface,vlan | jump.example.com | jumpuser     | jumppass      |
| 10.10.10.2        | netadmin | pass123  | ospf,bgp       | 172.16.1.100     | bastion_user | bastion_pass  |
| switch03.internal | admin    | secret   | lacp           | jump.example.com | jumpuser     | jumppass      |

**Completa las columnas Jump_Host, Jump_User y Jump_Password** con las credenciales del servidor de salto.

#### Descripción de las columnas

- **Name**: IP o hostname del dispositivo final
- **User**: Usuario SSH del dispositivo final
- **Password**: Contraseña SSH del dispositivo final
- **Parameter**: Parámetros a buscar (separados por comas)
- **Jump_Host**: *(Opcional)* IP o hostname del jump server
- **Jump_User**: *(Opcional)* Usuario SSH del jump server
- **Jump_Password**: *(Opcional)* Contraseña SSH del jump server

3. Guardar y cerrar Excel

### 3. Ejecutar automatización

1. Click en **"Run"**
2. El programa:
   - Si Jump_Host está configurado: establece un túnel SSH a través del jump server
   - Si Jump_Host está vacío: se conecta directamente desde tu máquina
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
Fecha: 2026-02-06 15:45:30
Total de comandos ejecutados: 5
Jump Server utilizado: jump.example.com (3 dispositivos)
Conexión directa: 2 dispositivos
======================================================================

✓ RESULTADOS EXITOSOS:
----------------------------------------------------------------------
  • Count for interface in 10.10.10.1 (via jump.example.com): 24
  • Count for vlan in 10.10.10.1 (via jump.example.com): 12
  • Count for ospf in 10.10.10.2 (via 172.16.1.100): 8
  • Count for bgp in router02.wan (direct): 15
  • Count for lacp in switch01.lan (direct): 6

======================================================================
RESUMEN:
  • Comandos exitosos: 5
  • Comandos fallidos: 0
  • Total de líneas encontradas: 65
  • Conexiones vía jump server: 3
  • Conexiones directas: 2
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
│   │   └── ssh_service.py          # Conexiones SSH (con soporte jump server)
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

**Tipos soportados:**

- `cisco_ios`, `cisco_xe`, `cisco_xr`, `cisco_nxos`, `cisco_asa`
- `arista_eos`
- `juniper_junos`
- `hp_comware`, `hp_procurve`
- `huawei`

### Ajustar timeout de conexión

```python
def __init__(self, device_type: str = 'cisco_ios', timeout: int = 30):
```

### Configuración de Jump Server

El sistema detecta automáticamente si debe usar jump server:

- **Campos vacíos** (Jump_Host, Jump_User, Jump_Password): conexión directa
- **Campos completados**: establece túnel SSH automático a través del jump server

La implementación utiliza Paramiko para crear un canal SSH directo (ProxyJump) que permite conexiones transparentes a dispositivos internos.

## 🔒 Seguridad

⚠️ **No subas el archivo Excel con contraseñas a repositorios públicos**
⚠️ El archivo `Device_Data.xlsx` está excluido en `.gitignore`
⚠️ Las credenciales del jump server también deben protegerse adecuadamente
✅ Considera usar un gestor de credenciales para entornos de producción
✅ Las contraseñas nunca se imprimen en consola (se muestran como `*****`)
✅ Usa autenticación basada en claves SSH cuando sea posible

## 🐛 Troubleshooting

### Error de autenticación

- Verifica usuario y contraseña en el Excel (tanto del dispositivo como del jump server)
- Confirma que el usuario tiene permisos SSH en el dispositivo
- Si usas jump server, verifica que las credenciales del jump server sean correctas

### Timeout de conexión

- Verifica conectividad de red: `ping <dispositivo>`
- Si usas jump server: verifica conectividad al jump server: `ping <jump_host>`
- Asegúrate de que SSH está habilitado en el dispositivo
- Aumenta el timeout en `ssh_service.py`

### Error con Jump Server

- Verifica que el jump server tiene acceso a los dispositivos finales
- Confirma que el puerto SSH (22) está abierto en el jump server
- Revisa que el jump server permite port forwarding (`AllowTcpForwarding yes` en sshd_config)
- Verifica que no hay firewalls bloqueando la conexión

### Error "Excel no encontrado"

- Click en "Open Excel" para crear el archivo
- Verifica que el archivo existe en `data/Device_Data.xlsx`

### Error "Jump Server connection failed"

- Verifica credenciales del jump server
- Confirma conectividad: `ssh <Jump_User>@<Jump_Host>`
- Revisa logs para detalles específicos del error

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
- [Paramiko](https://github.com/paramiko/paramiko) - Implementación SSH para Python (jump server support)
- [openpyxl](https://openpyxl.readthedocs.io/) - Gestión de archivos Excel
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - Framework GUI

---

⭐ **Si este proyecto te ha sido útil, considera darle una estrella en GitHub**
