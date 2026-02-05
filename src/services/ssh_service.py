"""Servicio para gestionar conexiones SSH y ejecución de comandos."""
from typing import List, Dict
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
import time

from ..models.device import Device
from ..models.command_result import CommandResult


class SSHService:
    """Gestiona las conexiones SSH y ejecución de comandos en dispositivos de red."""
    
    # Mapeo de fabricantes comunes (puedes expandir según necesites)
    DEVICE_TYPE_MAP = {
        'cisco': 'cisco_ios',
        'arista': 'arista_eos',
        'juniper': 'juniper_junos',
        'hp': 'hp_comware',
        'huawei': 'huawei',
    }
    
    def __init__(self, device_type: str = 'cisco_ios', timeout: int = 30):
        """
        Inicializa el servicio SSH.
        
        Args:
            device_type: Tipo de dispositivo (por defecto cisco_ios)
            timeout: Timeout de conexión en segundos
        """
        self.device_type = device_type
        self.timeout = timeout
    
    def execute_commands_on_device(self, device: Device) -> List[CommandResult]:
        """
        Ejecuta comandos en un dispositivo específico.
        
        Args:
            device: Dispositivo donde ejecutar los comandos
            
        Returns:
            Lista de CommandResult con los resultados de cada comando
        """
        results = []
        parameters = device.get_parameters_list()
        
        if not parameters:
            print(f"⚠ No hay parámetros definidos para {device.name}")
            return results
        
        # Configuración de conexión
        device_config = {
            'device_type': self.device_type,
            'host': device.name,
            'username': device.user,
            'password': device.password,
            'timeout': self.timeout,
            'session_log': None,  # Puedes habilitar logging si lo necesitas
        }
        
        print(f"\n{'='*70}")
        print(f"📡 Conectando a {device.name}...")
        print(f"{'='*70}")
        
        try:
            # Establecer conexión SSH
            with ConnectHandler(**device_config) as ssh_connection:
                print(f"✓ Conexión exitosa a {device.name}")
                
                # Ejecutar cada comando (uno por parámetro)
                for param in parameters:
                    command = f"show configuration running-config | in {param}"
                    print(f"\n  → Ejecutando: {command}")
                    
                    try:
                        # Ejecutar comando
                        output = ssh_connection.send_command(
                            command,
                            expect_string=r'#',
                            read_timeout=20
                        )
                        
                        # Procesar output
                        result = self._process_command_output(
                            device.name,
                            param,
                            output
                        )
                        results.append(result)
                        
                        print(f"    ✓ Líneas encontradas: {result.line_count}")
                        
                        # Pequeña pausa entre comandos
                        time.sleep(0.5)
                        
                    except Exception as cmd_error:
                        error_msg = f"Error ejecutando comando: {str(cmd_error)}"
                        print(f"    ✗ {error_msg}")
                        results.append(CommandResult(
                            device_name=device.name,
                            parameter=param,
                            output_lines=[],
                            line_count=0,
                            success=False,
                            error_message=error_msg
                        ))
                
                print(f"\n✓ Comandos completados en {device.name}")
                
        except NetmikoAuthenticationException:
            error_msg = "Fallo de autenticación"
            print(f"✗ {error_msg} en {device.name}")
            self._add_error_results(results, device, parameters, error_msg)
            
        except NetmikoTimeoutException:
            error_msg = "Timeout de conexión"
            print(f"✗ {error_msg} al conectar a {device.name}")
            self._add_error_results(results, device, parameters, error_msg)
            
        except Exception as e:
            error_msg = str(e)
            print(f"✗ Error en {device.name}: {error_msg}")
            self._add_error_results(results, device, parameters, error_msg)
        
        return results
    
    def _process_command_output(
        self,
        device_name: str,
        parameter: str,
        output: str
    ) -> CommandResult:
        """
        Procesa el output de un comando y cuenta las líneas relevantes.
        
        Args:
            device_name: Nombre del dispositivo
            parameter: Parámetro buscado
            output: Output del comando
            
        Returns:
            CommandResult con el resultado procesado
        """
        # Dividir output en líneas
        all_lines = output.strip().split('\n')
        
        # Filtrar líneas vacías y líneas de sistema
        filtered_lines = []
        skip_patterns = [
            'Building configuration',
            'Current configuration',
            'Date:',
            '!',  # Comentarios de Cisco
        ]
        
        for line in all_lines:
            line_stripped = line.strip()
            
            # Saltar líneas vacías
            if not line_stripped:
                continue
            
            # Saltar líneas de sistema
            should_skip = False
            for pattern in skip_patterns:
                if pattern.lower() in line_stripped.lower():
                    should_skip = True
                    break
            
            if not should_skip:
                filtered_lines.append(line)
        
        # Contar líneas relevantes
        line_count = len(filtered_lines)
        
        return CommandResult(
            device_name=device_name,
            parameter=parameter,
            output_lines=filtered_lines,
            line_count=line_count,
            success=True
        )
    
    def _add_error_results(
        self,
        results: List[CommandResult],
        device: Device,
        parameters: List[str],
        error_message: str
    ) -> None:
        """Agrega resultados de error para todos los parámetros."""
        for param in parameters:
            results.append(CommandResult(
                device_name=device.name,
                parameter=param,
                output_lines=[],
                line_count=0,
                success=False,
                error_message=error_message
            ))
