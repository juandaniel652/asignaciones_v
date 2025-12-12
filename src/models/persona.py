# ============================================================================
# UBICACIÓN: src/models/persona.py
# ============================================================================

from dataclasses import dataclass
from typing import Optional
from enum import Enum

class TipoPersona(Enum):
    ACOMODADOR = "acomodador"
    VIGILANTE = "vigilante"

@dataclass
class Persona:
    """Modelo de datos para una persona (acomodador o vigilante)"""
    id: Optional[int] = None
    nombre: str = ""
    apellido: str = ""
    tipo: TipoPersona = TipoPersona.ACOMODADOR
    activo: bool = True
    grupo: Optional[int] = None  # Para vigilantes
    
    @property
    def nombre_completo(self) -> str:
        return f"{self.apellido} {self.nombre}"
    
    def __str__(self) -> str:
        return self.nombre_completo