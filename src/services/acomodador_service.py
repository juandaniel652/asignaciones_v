import random
import sqlite3
from typing import List, Tuple
from src.models.persona import Persona, TipoPersona
from src.database.repositories.persona_repository import PersonaRepository

class AcomodadorService:
    """Patrón Service: Contiene la lógica de negocio de acomodadores"""
    
    def __init__(self, repository: PersonaRepository = None):
        self.repository = repository or PersonaRepository()
    
    def obtener_acomodadores_activos(self) -> List[Persona]:
        """Obtiene todos los acomodadores activos ordenados"""
        return self.repository.obtener_todos(TipoPersona.ACOMODADOR)
    
    def seleccionar_aleatorios(self, cantidad: int = 5) -> Tuple[List[Persona], str]:
        """
        Selecciona acomodadores aleatoriamente
        Returns: (lista_seleccionados, mensaje_formateado)
        """
        acomodadores = self.obtener_acomodadores_activos()
        
        if len(acomodadores) < cantidad:
            raise ValueError(f"Se necesitan al menos {cantidad} acomodadores activos. Actualmente hay {len(acomodadores)}.")
        
        seleccionados = random.sample(acomodadores, cantidad)
        
        mensaje = self._formatear_seleccion(seleccionados)
        return seleccionados, mensaje
    
    def _formatear_seleccion(self, seleccionados: List[Persona]) -> str:
        """Formatea la selección para mostrar"""
        return (
            f"Acomodadores 1° hora: {seleccionados[0]} / {seleccionados[1]}\n\n"
            f"Acomodadores 2° hora: {seleccionados[2]} / {seleccionados[3]}\n\n"
            f"Acomodador después de la reunión: {seleccionados[4]}"
        )
    
    def desactivar_acomodador(self, persona_id: int):
        """Desactiva un acomodador (equivalente a remover)"""
        self.repository.desactivar(persona_id)
    
    def reiniciar_todos(self) -> List[Persona]:
        """Reactiva todos los acomodadores"""
        # Primero obtener todos (incluso inactivos)
        with sqlite3.connect(self.repository.db_path) as conn:
            cursor = conn.execute(
                "SELECT id FROM personas WHERE tipo = ?",
                (TipoPersona.ACOMODADOR.value,)
            )
            for row in cursor.fetchall():
                self.repository.activar(row[0])
        
        return self.obtener_acomodadores_activos()
    
    def agregar_acomodador(self, nombre: str, apellido: str) -> Persona:
        """Agrega un nuevo acomodador"""
        persona = Persona(
            nombre=nombre,
            apellido=apellido,
            tipo=TipoPersona.ACOMODADOR,
            activo=True
        )
        persona.id = self.repository.agregar(persona)
        return persona
    
    def validar_cantidad_minima(self, minimo: int = 5) -> Tuple[bool, str]:
        """Valida que haya suficientes acomodadores activos"""
        activos = self.obtener_acomodadores_activos()
        es_valido = len(activos) >= minimo
        mensaje = f"Hay {len(activos)} acomodadores activos. Se necesitan al menos {minimo}."
        return es_valido, mensaje