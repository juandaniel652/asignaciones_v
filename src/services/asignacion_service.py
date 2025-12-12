from typing import List, Optional
from src.models.asignacion import Asignacion
from src.models.persona import Persona
from src.models.semana import Semana
from src.database.repositories.asignacion_repository import AsignacionRepository

class AsignacionService:
    """Servicio para gestionar lógica de negocio de asignaciones"""
    
    def __init__(self, repository: AsignacionRepository = None):
        self.repository = repository or AsignacionRepository()
    
    def crear_asignacion(self, semana: Semana,
                        acomodadores: List[Persona],
                        vigilantes: List[Persona],
                        tipo_reunion: str = "entre_semana") -> Asignacion:
        """
        Crea una asignación completa
        Args:
            semana: Objeto Semana
            acomodadores: Lista con 5 personas [1h_1, 1h_2, 2h_1, 2h_2, final]
            vigilantes: Lista con 3 personas [1h, 2h, final]
            tipo_reunion: "entre_semana" o "fin_semana"
        """
        if len(acomodadores) != 5:
            raise ValueError("Se necesitan exactamente 5 acomodadores")
        
        if len(vigilantes) != 3:
            raise ValueError("Se necesitan exactamente 3 vigilantes")
        
        # Formatear día de reunión
        if tipo_reunion == "entre_semana":
            tipo, fecha = semana.dia_reunion_entre_semana
            dia_reunion = f"{tipo.value.capitalize()} {fecha.day}"
        else:
            tipo, fecha = semana.dia_reunion_fin_semana
            dia_reunion = f"{tipo.value.capitalize()} {fecha.day}"
        
        asignacion = Asignacion(
            semana=semana,
            acomodador_1hora_1=acomodadores[0],
            acomodador_1hora_2=acomodadores[1],
            acomodador_2hora_1=acomodadores[2],
            acomodador_2hora_2=acomodadores[3],
            acomodador_final=acomodadores[4],
            vigilante_1hora=vigilantes[0],
            vigilante_2hora=vigilantes[1],
            vigilante_final=vigilantes[2],
            dia_reunion=dia_reunion
        )
        
        return asignacion
    
    def guardar_asignacion(self, asignacion: Asignacion) -> tuple[bool, str]:
        """
        Guarda una asignación en la BD
        Returns: (exito, mensaje)
        """
        # Validar
        es_valida, mensaje = asignacion.validar()
        if not es_valida:
            return False, f"Asignación inválida: {mensaje}"
        
        try:
            id_asignacion = self.repository.guardar(asignacion)
            return True, f"Asignación guardada con ID {id_asignacion}"
        except Exception as e:
            return False, f"Error al guardar: {e}"
    
    def obtener_todas_asignaciones(self) -> List[tuple]:
        """Obtiene todas las asignaciones para mostrar en TreeView"""
        return self.repository.obtener_todas()
    
    def obtener_asignaciones_por_mes(self, numero_mes: int) -> List[tuple]:
        """Obtiene asignaciones de un mes específico"""
        if numero_mes < 1 or numero_mes > 12:
            raise ValueError("El mes debe estar entre 1 y 12")
        
        return self.repository.obtener_por_mes(numero_mes)
    
    def limpiar_todas_asignaciones(self) -> bool:
        """Elimina todas las asignaciones"""
        try:
            self.repository.eliminar_todas()
            return True
        except Exception as e:
            print(f"Error al limpiar: {e}")
            return False
