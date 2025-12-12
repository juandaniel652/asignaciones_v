from datetime import date, timedelta
from typing import List, Tuple, Dict, Optional
from src.models.semana import Semana, TipoSemana
from src.utils.date_utils import DateUtils
from src.services.grupo_limpieza_service import GrupoLimpiezaService

class FechaService:
    """Servicio principal para gestión de fechas y semanas"""
    
    def __init__(self):
        self.date_utils = DateUtils()
        self.grupo_service = GrupoLimpiezaService()
        
        # Configurar locale
        self.date_utils.configurar_locale_espanol()
        
        # Fechas especiales (asambleas, convenciones)
        self.eventos_especiales = [
            {
                'fecha': date(2025, 10, 31),
                'tipo': TipoSemana.ASAMBLEA,
                'nombre': 'Asamblea Regional 2025\n\n         Adoración Pura\n(Mat. 4:10; Juan. 2:17; Juan. 4:23)'
            },
            {
                'fecha': date(2026, 3, 22),
                'tipo': TipoSemana.CIRCUITO,
                'nombre': 'Asamblea de circuito con el\nrepresentante de la sucursal'
            }
        ]
        
        # Días especiales de reunión (diferentes a los habituales)
        self.dias_especiales_entre_semana = [
            date(2025, 7, 7),   # Martes en vez de miércoles
            date(2026, 4, 2)
        ]
        
        self.dias_especiales_fin_semana = []  # Sábados en vez de domingos
    
    def generar_semanas(self, fecha_inicio: Optional[date] = None, 
                       cantidad: int = 52) -> List[Semana]:
        """
        Genera la lista completa de semanas
        Args:
            fecha_inicio: Fecha de inicio (si es None, usa hoy)
            cantidad: Cantidad de semanas a generar
        Returns:
            Lista de objetos Semana
        """
        if fecha_inicio is None:
            fecha_inicio = date.today()
        
        # Encontrar el lunes de la semana actual
        primer_lunes = self.date_utils.buscar_lunes(fecha_inicio)
        
        # Generar lista de lunes
        lunes_list = self.date_utils.generar_semanas(primer_lunes, cantidad)
        
        # Obtener secuencia de grupos de limpieza
        grupos = self.grupo_service.obtener_secuencia_grupos(primer_lunes, cantidad)
        
        # Crear objetos Semana
        semanas = []
        for i, lunes in enumerate(lunes_list):
            semana = self._crear_semana(lunes, i + 1, grupos[i])
            semanas.append(semana)
        
        return semanas
    
    def _crear_semana(self, lunes: date, numero: int, grupo: int) -> Semana:
        """Crea un objeto Semana con todos sus datos"""
        # Días normales
        miercoles = lunes + timedelta(days=2)
        domingo = lunes + timedelta(days=6)
        
        # Verificar si tiene días especiales
        martes = None
        sabado = None
        
        martes_fecha = lunes + timedelta(days=1)
        sabado_fecha = lunes + timedelta(days=5)
        
        if martes_fecha in self.dias_especiales_entre_semana:
            martes = martes_fecha
        
        if sabado_fecha in self.dias_especiales_fin_semana:
            sabado = sabado_fecha
        
        # Verificar si es semana especial
        tipo = TipoSemana.NORMAL
        nombre_evento = None
        
        for evento in self.eventos_especiales:
            if self.date_utils.es_misma_semana(lunes, evento['fecha']):
                tipo = evento['tipo']
                nombre_evento = evento['nombre']
                break
        
        return Semana(
            lunes=lunes,
            numero=numero,
            grupo_limpieza=grupo,
            miercoles=miercoles,
            domingo=domingo,
            martes=martes,
            sabado=sabado,
            tipo=tipo,
            nombre_evento=nombre_evento
        )
    
    def obtener_semana_actual(self, semanas: List[Semana]) -> Optional[Semana]:
        """Obtiene la semana actual de la lista"""
        hoy = date.today()
        lunes_actual = self.date_utils.buscar_lunes(hoy)
        
        for semana in semanas:
            if semana.lunes == lunes_actual:
                return semana
        return None
    
    def filtrar_semanas_especiales(self, semanas: List[Semana]) -> List[Semana]:
        """Filtra solo las semanas especiales"""
        return [s for s in semanas if s.es_especial]
    
    def obtener_proximas_semanas(self, semanas: List[Semana], 
                                cantidad: int = 4) -> List[Semana]:
        """Obtiene las próximas N semanas desde hoy"""
        hoy = date.today()
        return [s for s in semanas if s.lunes >= hoy][:cantidad]
    
    def calcular_distancia_entre_eventos(self, semanas: List[Semana]) -> Dict[str, int]:
        """
        Calcula la distancia en semanas entre eventos especiales
        Returns: Dict con distancias
        """
        especiales = self.filtrar_semanas_especiales(semanas)
        distancias = {}
        
        for i in range(len(especiales) - 1):
            semana1 = especiales[i]
            semana2 = especiales[i + 1]
            
            distancia = self.date_utils.calcular_distancia_semanas(
                semana1.lunes, semana2.lunes
            )
            
            key = f"{semana1.nombre_evento[:20]}... → {semana2.nombre_evento[:20]}..."
            distancias[key] = distancia
        
        return distancias
    
    def formatear_para_listbox(self, semanas: List[Semana]) -> List[str]:
        """Formatea las semanas para mostrar en un Listbox"""
        return [str(semana) for semana in semanas]
    
    def formatear_dia_reunion(self, semana: Semana, 
                             tipo_dia: str = "entre_semana") -> str:
        """
        Formatea el día de reunión para mostrar
        Args:
            semana: Objeto Semana
            tipo_dia: "entre_semana" o "fin_semana"
        Returns:
            String formateado (ej: "Miércoles 15")
        """
        if tipo_dia == "entre_semana":
            tipo, fecha = semana.dia_reunion_entre_semana
            return f"{tipo.value.capitalize()} {fecha.day}"
        else:
            tipo, fecha = semana.dia_reunion_fin_semana
            return f"{tipo.value.capitalize()} {fecha.day}"