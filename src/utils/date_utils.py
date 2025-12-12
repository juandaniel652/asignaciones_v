from datetime import date, timedelta
from typing import List, Tuple
import locale

class DateUtils:
    """Utilidades para manejo de fechas"""
    
    @staticmethod
    def configurar_locale_espanol():
        """Configura el locale en español"""
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES.utf8')
        except:
            try:
                locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
            except:
                pass  # Continuar sin locale español
    
    @staticmethod
    def buscar_lunes(fecha: date) -> date:
        """
        Encuentra el lunes de la semana de una fecha dada
        Args:
            fecha: Fecha cualquiera
        Returns:
            Fecha del lunes de esa semana
        """
        dias_desde_lunes = fecha.weekday()  # 0=Lunes, 6=Domingo
        return fecha - timedelta(days=dias_desde_lunes)
    
    @staticmethod
    def obtener_dia_semana(fecha: date, dia_target: int) -> date:
        """
        Obtiene un día específico de la semana
        Args:
            fecha: Fecha base (lunes)
            dia_target: 0=Lunes, 1=Martes, 2=Miércoles, 6=Domingo
        Returns:
            Fecha del día solicitado
        """
        return fecha + timedelta(days=dia_target)
    
    @staticmethod
    def generar_semanas(fecha_inicio: date, cantidad: int) -> List[date]:
        """
        Genera una lista de lunes consecutivos
        Args:
            fecha_inicio: Primer lunes
            cantidad: Cantidad de semanas
        Returns:
            Lista de fechas (lunes)
        """
        return [fecha_inicio + timedelta(weeks=i) for i in range(cantidad)]
    
    @staticmethod
    def calcular_distancia_semanas(fecha1: date, fecha2: date) -> int:
        """
        Calcula la distancia en semanas entre dos fechas
        Args:
            fecha1: Primera fecha
            fecha2: Segunda fecha
        Returns:
            Número de semanas de diferencia
        """
        diferencia = fecha2 - fecha1
        return diferencia.days // 7
    
    @staticmethod
    def es_misma_semana(fecha1: date, fecha2: date) -> bool:
        """
        Verifica si dos fechas están en la misma semana
        """
        lunes1 = DateUtils.buscar_lunes(fecha1)
        lunes2 = DateUtils.buscar_lunes(fecha2)
        return lunes1 == lunes2