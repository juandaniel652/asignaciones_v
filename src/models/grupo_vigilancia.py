from dataclasses import dataclass
from typing import List
from src.models.persona import Persona

@dataclass
class GrupoVigilancia:
    """Modelo para agrupar vigilantes"""
    numero: int
    miembros: List[Persona]
    
    def contiene_persona(self, persona: Persona) -> bool:
        """Verifica si una persona pertenece al grupo"""
        return persona in self.miembros
    
    def obtener_nombres(self) -> List[str]:
        """Retorna los nombres completos del grupo"""
        return [str(p) for p in self.miembros]
    
    def __len__(self) -> int:
        return len(self.miembros)