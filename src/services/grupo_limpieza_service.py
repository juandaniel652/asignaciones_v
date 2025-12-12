from typing import List
from datetime import date

class GrupoLimpiezaService:
    """Servicio para gestionar la rotación de grupos de limpieza"""
    
    def __init__(self):
        # Ciclo de grupos: 6, 5, 4, 3, 2, 1 (rotación inversa)
        self.ciclo_grupos = [6, 5, 4, 3, 2, 1]
        
        # Fecha de referencia para el grupo 1
        # En esta fecha comienza el grupo 1
        self.fecha_referencia = date(2033, 2, 7)  # Domingo
        self.grupo_referencia = 1
    
    def obtener_grupo_para_semana(self, lunes: date) -> int:
        """
        Calcula qué grupo de limpieza corresponde a una semana
        Args:
            lunes: Fecha del lunes de la semana
        Returns:
            Número de grupo (1-6)
        """
        # Calcular semanas desde la fecha de referencia
        diferencia = self.fecha_referencia - lunes
        semanas = diferencia.days // 7
        
        # Calcular posición en el ciclo
        posicion = semanas % len(self.ciclo_grupos)
        
        return self.ciclo_grupos[posicion]
    
    def obtener_secuencia_grupos(self, fecha_inicio: date, cantidad: int) -> List[int]:
        """
        Obtiene la secuencia de grupos para varias semanas
        Args:
            fecha_inicio: Primer lunes
            cantidad: Cantidad de semanas
        Returns:
            Lista de números de grupo
        """
        from datetime import timedelta
        grupos = []
        
        for i in range(cantidad):
            lunes = fecha_inicio + timedelta(weeks=i)
            grupo = self.obtener_grupo_para_semana(lunes)
            grupos.append(grupo)
        
        return grupos
    
    def ajustar_grupo_por_evento_especial(self, grupo_actual: int, 
                                         semanas_salteadas: int) -> int:
        """
        Ajusta el grupo cuando hay eventos especiales que saltean semanas
        Args:
            grupo_actual: Grupo que correspondería normalmente
            semanas_salteadas: Cantidad de semanas que se saltean
        Returns:
            Número de grupo ajustado
        """
        # Avanzar en el ciclo según las semanas salteadas
        indice_actual = self.ciclo_grupos.index(grupo_actual)
        nuevo_indice = (indice_actual + semanas_salteadas) % len(self.ciclo_grupos)
        return self.ciclo_grupos[nuevo_indice]