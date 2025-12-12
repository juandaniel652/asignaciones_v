from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional
from enum import Enum

class TipoDia(Enum):
    """Tipo de día de reunión"""
    MIERCOLES = "miércoles"
    DOMINGO = "domingo"
    MARTES = "martes"
    SABADO = "sábado"

class TipoSemana(Enum):
    """Tipo de semana especial"""
    NORMAL = "normal"
    ASAMBLEA = "asamblea"
    CONVENCION = "convencion"
    CIRCUITO = "circuito"

@dataclass
class Semana:
    """Modelo de datos para una semana"""
    lunes: date
    numero: int
    grupo_limpieza: int
    
    # Días de reunión
    miercoles: date
    domingo: date
    martes: Optional[date] = None
    sabado: Optional[date] = None
    
    # Información especial
    tipo: TipoSemana = TipoSemana.NORMAL
    nombre_evento: Optional[str] = None
    
    @property
    def texto_completo(self) -> str:
        """Formato: '6-12 enero 2025'"""
        inicio = self.lunes
        fin = inicio + timedelta(days=6)
        
        if inicio.month == fin.month:
            return f"{inicio.day}-{fin.day} {self._nombre_mes(inicio.month)} {inicio.year}"
        else:
            return f"{inicio.day} {self._nombre_mes(inicio.month)} - {fin.day} {self._nombre_mes(fin.month)} {inicio.year}"
    
    @property
    def dia_reunion_entre_semana(self) -> tuple[TipoDia, date]:
        """Retorna el día de reunión entre semana (martes o miércoles)"""
        if self.martes:
            return (TipoDia.MARTES, self.martes)
        return (TipoDia.MIERCOLES, self.miercoles)
    
    @property
    def dia_reunion_fin_semana(self) -> tuple[TipoDia, date]:
        """Retorna el día de reunión fin de semana (sábado o domingo)"""
        if self.sabado:
            return (TipoDia.SABADO, self.sabado)
        return (TipoDia.DOMINGO, self.domingo)
    
    @property
    def es_especial(self) -> bool:
        """Indica si es una semana especial"""
        return self.tipo != TipoSemana.NORMAL
    
    def _nombre_mes(self, mes: int) -> str:
        """Retorna el nombre del mes en español"""
        meses = [
            "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        ]
        return meses[mes]
    
    def __str__(self) -> str:
        return self.texto_completo