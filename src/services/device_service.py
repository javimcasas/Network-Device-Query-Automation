"""Servicio para gestionar operaciones con dispositivos de red."""
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from ..models.device import Device
from ..models.command_result import CommandResult
from ..services.ssh_service import SSHService
from ..config.constants import DATA_DIR


class DeviceService:
    """Gestiona las operaciones relacionadas con dispositivos de red."""
    
    def __init__(self):
        """Inicializa el servicio de dispositivos."""
        self.ssh_service = SSHService()
    
    def print_devices(self, devices: List[Device]) -> None:
        """Imprime la información de los dispositivos columna por columna."""
        if not devices:
            print("\n⚠ No hay dispositivos registrados en el Excel\n")
            return
        
        print("\n" + "="*80)
        print(f"{'DISPOSITIVOS REGISTRADOS':^80}")
        print("="*80 + "\n")
        
        for idx, device in enumerate(devices, 1):
            print(f"--- Dispositivo {idx} ---")
            print(f"  Name:      {device.name}")
            print(f"  User:      {device.user}")
            print(f"  Password:  {'*' * len(device.password)}")
            print(f"  Parameter: {device.parameter}")
            print(f"  Params:    {device.get_parameters_list()}")
            print()
        
        print("="*80)
        print(f"Total de dispositivos: {len(devices)}\n")
    
    def execute_automation(
        self,
        devices: List[Device],
        jump_host: Optional[str] = None,
        jump_user: Optional[str] = None,
        jump_pass: Optional[str] = None,
    ) -> Path:
        """
        Ejecuta la automatización sobre los dispositivos.
        """
        print("\n🚀 Iniciando proceso de automatización...\n")
        
        if not devices:
            print("⚠ No hay dispositivos para procesar\n")
            raise ValueError("No hay dispositivos registrados")
        
        print(f"📋 Dispositivos a procesar: {len(devices)}")
        for device in devices:
            params = device.get_parameters_list()
            print(f"  • {device.name} ({len(params)} parámetros)")
        print()
        
        all_results: List[CommandResult] = []
        
        for idx, device in enumerate(devices, 1):
            print(f"\n[{idx}/{len(devices)}] Procesando {device.name}...")
            results = self.ssh_service.execute_commands_on_device(
                device,
                jump_host=jump_host,
                jump_user=jump_user,
                jump_pass=jump_pass,
            )
            all_results.extend(results)
        
        output_file = self._generate_output_file(all_results)
        
        print(f"\n{'='*70}")
        print("✓ Proceso completado exitosamente")
        print(f"📄 Resultados guardados en: {output_file}")
        print(f"{'='*70}\n")
        
        return output_file
    
    def _generate_output_file(self, results: List[CommandResult]) -> Path:
        """
        Genera el archivo de resultados con el conteo de líneas.
        
        Args:
            results: Lista de resultados de comandos
            
        Returns:
            Path al archivo generado
        """
        # Generar timestamp legible
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output_{timestamp}.txt"
        output_path = DATA_DIR / filename
        
        # Asegurar que existe el directorio
        DATA_DIR.mkdir(exist_ok=True)
        
        # Escribir resultados
        with open(output_path, 'w', encoding='utf-8') as f:
            # Encabezado
            f.write("="*70 + "\n")
            f.write(f"{'NETWORK AUTOMATION RESULTS':^70}\n")
            f.write("="*70 + "\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total de comandos ejecutados: {len(results)}\n")
            f.write("="*70 + "\n\n")
            
            # Resultados exitosos
            successful_results = [r for r in results if r.success]
            if successful_results:
                f.write("✓ RESULTADOS EXITOSOS:\n")
                f.write("-"*70 + "\n")
                for result in successful_results:
                    f.write(f"  • Count for {result.parameter} in {result.device_name}: {result.line_count}\n")
                f.write("\n")
            
            # Errores
            failed_results = [r for r in results if not r.success]
            if failed_results:
                f.write("✗ ERRORES:\n")
                f.write("-"*70 + "\n")
                for result in failed_results:
                    f.write(f"  • {result.device_name} ({result.parameter}): {result.error_message}\n")
                f.write("\n")
            
            # Resumen
            f.write("="*70 + "\n")
            f.write("RESUMEN:\n")
            f.write(f"  • Comandos exitosos: {len(successful_results)}\n")
            f.write(f"  • Comandos fallidos: {len(failed_results)}\n")
            f.write(f"  • Total de líneas encontradas: {sum(r.line_count for r in successful_results)}\n")
            f.write("="*70 + "\n")
        
        print(f"\n✓ Archivo generado: {output_path}")
        return output_path
