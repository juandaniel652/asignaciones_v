from dataclasses import dataclass
from typing import Optional
from datetime import date
from src.models.persona import Persona
from src.models.semana import Semana

@dataclass
class Asignacion:
    """Modelo de datos para una asignación completa"""
    id: Optional[int] = None
    semana: Semana = None
    
    # Acomodadores
    acomodador_1hora_1: Persona = None
    acomodador_1hora_2: Persona = None
    acomodador_2hora_1: Persona = None
    acomodador_2hora_2: Persona = None
    acomodador_final: Persona = None
    
    # Vigilantes
    vigilante_1hora: Persona = None
    vigilante_2hora: Persona = None
    vigilante_final: Persona = None
    
    # Día de reunión
    dia_reunion: str = ""
    
    @property
    def acomodadores_1hora(self) -> str:
        """Formatea acomodadores de primera hora"""
        if self.acomodador_1hora_1 and self.acomodador_1hora_2:
            return f"{self.acomodador_1hora_1} / {self.acomodador_1hora_2}"
        return ""
    
    @property
    def acomodadores_2hora(self) -> str:
        """Formatea acomodadores de segunda hora"""
        if self.acomodador_2hora_1 and self.acomodador_2hora_2:
            return f"{self.acomodador_2hora_1} / {self.acomodador_2hora_2}"
        return ""
    
    def to_tuple(self) -> tuple:
        """Convierte a tupla para TreeView"""
        return (
            str(self.semana),
            self.acomodadores_1hora,
            self.acomodadores_2hora,
            str(self.acomodador_final) if self.acomodador_final else "",
            str(self.vigilante_1hora) if self.vigilante_1hora else "",
            str(self.vigilante_2hora) if self.vigilante_2hora else "",
            str(self.vigilante_final) if self.vigilante_final else "",
            self.dia_reunion
        )
    
    def validar(self) -> tuple[bool, str]:
        """
        Valida que la asignación esté completa
        Returns: (es_valido, mensaje_error)
        """
        if not self.semana:
            return False, "Falta la semana"
        
        if not all([self.acomodador_1hora_1, self.acomodador_1hora_2, 
                   self.acomodador_2hora_1, self.acomodador_2hora_2, 
                   self.acomodador_final]):
            return False, "Faltan acomodadores"
        
        if not all([self.vigilante_1hora, self.vigilante_2hora, self.vigilante_final]):
            return False, "Faltan vigilantes"
        
        if not self.dia_reunion:
            return False, "Falta el día de reunión"
        
        return True, "OK"