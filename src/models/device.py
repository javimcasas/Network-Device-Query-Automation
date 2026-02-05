"""Modelo de datos para dispositivos de red."""
from dataclasses import dataclass
from typing import List


@dataclass
class Device:
    """Representa un dispositivo de red."""
    name: str
    user: str
    password: str
    parameter: str
    
    def get_parameters_list(self) -> List[str]:
        """Retorna la lista de parámetros separados por comas."""
        if not self.parameter or self.parameter.strip() == '':
            return []
        # Limpiar espacios y separar por comas
        return [p.strip() for p in self.parameter.split(',') if p.strip()]
    
    def __str__(self) -> str:
        """Representación string del dispositivo (oculta password)."""
        return (f"Device(name={self.name}, user={self.user}, "
                f"password=*****, parameter={self.parameter})")
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Device':
        """Crea un Device desde un diccionario."""
        return cls(
            name=data.get('Name', ''),
            user=data.get('User', ''),
            password=data.get('Password', ''),
            parameter=str(data.get('Parameter', ''))
        )
