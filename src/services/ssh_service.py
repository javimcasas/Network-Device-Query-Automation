"""Servicio para gestionar conexiones SSH y ejecución de comandos."""
from typing import List, Optional
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
import paramiko
import time

from ..models.device import Device
from ..models.command_result import CommandResult


class SSHService:
    """Gestiona las conexiones SSH y ejecución de comandos en dispositivos de red."""
    
    DEVICE_TYPE_MAP = {
        "cisco": "cisco_ios",
        "arista": "arista_eos",
        "juniper": "juniper_junos",
        "hp": "hp_comware",
        "huawei": "huawei",
    }
    
    def __init__(self, device_type: str = "cisco_ios", timeout: int = 30):
        self.device_type = device_type
        self.timeout = timeout
    
    def execute_commands_on_device(
        self,
        device: Device,
        jump_host: Optional[str] = None,
        jump_user: Optional[str] = None,
        jump_pass: Optional[str] = None,
    ) -> List[CommandResult]:
        """
        Ejecuta comandos en un dispositivo, opcionalmente a través de jump host.
        """
        results: List[CommandResult] = []
        parameters = device.get_parameters_list()
        
        if not parameters:
            print(f"⚠ No hay parámetros definidos para {device.name}")
            return results
        
        print(f"\n{'='*70}")
        print(f"📡 Conectando a {device.name}...")
        print(f"{'='*70}")
        
        jump_client = None
        channel = None
        
        try:
            # Si hay jump host configurado (host + user + pass), usamos túnel Paramiko
            if jump_host and jump_user and jump_pass:
                print(f"→ Usando jump host: {jump_host}")
                
                jump_client = paramiko.SSHClient()
                jump_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                jump_client.connect(
                    jump_host,
                    username=jump_user,
                    password=jump_pass,
                    timeout=self.timeout,
                )
                
                transport = jump_client.get_transport()
                dest_addr = (device.name, 22)
                local_addr = ("127.0.0.1", 0)
                channel = transport.open_channel(
                    "direct-tcpip", dest_addr, local_addr
                )
                
                device_config = {
                    "device_type": self.device_type,
                    "host": device.name,
                    "username": device.user,
                    "password": device.password,
                    "timeout": self.timeout,
                    "sock": channel,  # túnel a través del jump host
                }
            else:
                # Conexión directa con Netmiko
                device_config = {
                    "device_type": self.device_type,
                    "host": device.name,
                    "username": device.user,
                    "password": device.password,
                    "timeout": self.timeout,
                }
            
            with ConnectHandler(**device_config) as ssh_connection:
                print(f"✓ Conexión exitosa a {device.name}")
                
                for param in parameters:
                    command = f"show configuration running-config | in {param}"
                    print(f"\n  → Ejecutando: {command}")
                    
                    try:
                        output = ssh_connection.send_command(
                            command,
                            expect_string=r"#",
                            read_timeout=20,
                        )
                        
                        result = self._process_command_output(
                            device.name,
                            param,
                            output,
                        )
                        results.append(result)
                        
                        print(f"    ✓ Líneas encontradas: {result.line_count}")
                        time.sleep(0.5)
                    
                    except Exception as cmd_error:
                        error_msg = f"Error ejecutando comando: {str(cmd_error)}"
                        print(f"    ✗ {error_msg}")
                        results.append(
                            CommandResult(
                                device_name=device.name,
                                parameter=param,
                                output_lines=[],
                                line_count=0,
                                success=False,
                                error_message=error_msg,
                            )
                        )
            
            print(f"\n✓ Comandos completados en {device.name}")
        
        except NetmikoAuthenticationException:
            error_msg = "Fallo de autenticación"
            print(f"✗ {error_msg} en {device.name}")
            self._add_error_results(results, device, parameters, error_message=error_msg)
        
        except NetmikoTimeoutException:
            error_msg = "Timeout de conexión"
            print(f"✗ {error_msg} al conectar a {device.name}")
            self._add_error_results(results, device, parameters, error_message=error_msg)
        
        except Exception as e:
            error_msg = str(e)
            print(f"✗ Error en {device.name}: {error_msg}")
            self._add_error_results(results, device, parameters, error_message=error_msg)
        
        finally:
            try:
                if channel is not None:
                    channel.close()
                if jump_client is not None:
                    jump_client.close()
            except Exception:
                pass
        
        return results
    
    def _process_command_output(
        self,
        device_name: str,
        parameter: str,
        output: str,
    ) -> CommandResult:
        """Procesa el output y cuenta líneas relevantes."""
        all_lines = output.strip().split("\n")
        
        filtered_lines = []
        skip_patterns = [
            "Building configuration",
            "Current configuration",
            "Date:",
            "!",  # Comentarios de Cisco
        ]
        
        for line in all_lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            if any(pat.lower() in line_stripped.lower() for pat in skip_patterns):
                continue
            
            filtered_lines.append(line)
        
        line_count = len(filtered_lines)
        
        return CommandResult(
            device_name=device_name,
            parameter=parameter,
            output_lines=filtered_lines,
            line_count=line_count,
            success=True,
        )
    
    def _add_error_results(
        self,
        results: List[CommandResult],
        device: Device,
        parameters: List[str],
        error_message: str,
    ) -> None:
        """Agrega resultados de error para todos los parámetros."""
        for param in parameters:
            results.append(
                CommandResult(
                    device_name=device.name,
                    parameter=param,
                    output_lines=[],
                    line_count=0,
                    success=False,
                    error_message=error_message,
                )
            )
