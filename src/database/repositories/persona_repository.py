import sqlite3
from typing import List, Optional
from src.models.persona import Persona, TipoPersona

class PersonaRepository:
    """Patrón Repository: Maneja el acceso a datos de personas"""
    
    def __init__(self, db_path: str = "asignaciones.db"):
        self.db_path = db_path
        self._crear_tabla()
    
    def _crear_tabla(self):
        """Crea la tabla si no existe"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS personas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    apellido TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    activo INTEGER DEFAULT 1,
                    grupo INTEGER
                )
            """)
    
    def obtener_todos(self, tipo: TipoPersona) -> List[Persona]:
        """Obtiene todas las personas de un tipo"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM personas WHERE tipo = ? AND activo = 1 ORDER BY apellido, nombre",
                (tipo.value,)
            )
            return [self._row_to_persona(row) for row in cursor.fetchall()]
    
    def agregar(self, persona: Persona) -> int:
        """Agrega una nueva persona"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO personas (nombre, apellido, tipo, activo, grupo) VALUES (?, ?, ?, ?, ?)",
                (persona.nombre, persona.apellido, persona.tipo.value, persona.activo, persona.grupo)
            )
            return cursor.lastrowid
    
    def desactivar(self, persona_id: int):
        """Desactiva una persona (soft delete)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE personas SET activo = 0 WHERE id = ?", (persona_id,))
    
    def activar(self, persona_id: int):
        """Reactiva una persona"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE personas SET activo = 1 WHERE id = ?", (persona_id,))
    
    def _row_to_persona(self, row) -> Persona:
        """Convierte una fila de BD a objeto Persona"""
        return Persona(
            id=row[0],
            nombre=row[1],
            apellido=row[2],
            tipo=TipoPersona(row[3]),
            activo=bool(row[4]),
            grupo=row[5]
        )
