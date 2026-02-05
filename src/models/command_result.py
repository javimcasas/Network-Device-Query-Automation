"""Modelo para resultados de comandos SSH."""
from dataclasses import dataclass
from typing import List


@dataclass
class CommandResult:
    """Representa el resultado de ejecutar un comando en un dispositivo."""
    device_name: str
    parameter: str
    output_lines: List[str]
    line_count: int
    success: bool
    error_message: str = ""
    
    def __str__(self) -> str:
        """Representación string del resultado."""
        if self.success:
            return f"Count for {self.parameter} in {self.device_name}: {self.line_count}"
        else:
            return f"Error for {self.parameter} in {self.device_name}: {self.error_message}"
