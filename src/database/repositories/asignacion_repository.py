import sqlite3
from typing import List, Optional
from datetime import date
from src.models.asignacion import Asignacion
from src.models.persona import Persona
from src.models.semana import Semana

class AsignacionRepository:
    """Repository para gestionar asignaciones en la BD"""
    
    def __init__(self, db_path: str = "asignaciones.db"):
        self.db_path = db_path
        self._crear_tabla()
    
    def _crear_tabla(self):
        """Crea la tabla de asignaciones si no existe"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS asignaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    semana TEXT NOT NULL,
                    acomodadores_1hora TEXT NOT NULL,
                    acomodadores_2hora TEXT NOT NULL,
                    acomodador_final TEXT NOT NULL,
                    vigilante_1hora TEXT NOT NULL,
                    vigilante_2hora TEXT NOT NULL,
                    vigilante_final TEXT NOT NULL,
                    dia_reunion TEXT NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def guardar(self, asignacion: Asignacion) -> int:
        """Guarda una asignación en la BD"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO asignaciones 
                (semana, acomodadores_1hora, acomodadores_2hora, acomodador_final,
                 vigilante_1hora, vigilante_2hora, vigilante_final, dia_reunion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(asignacion.semana),
                asignacion.acomodadores_1hora,
                asignacion.acomodadores_2hora,
                str(asignacion.acomodador_final),
                str(asignacion.vigilante_1hora),
                str(asignacion.vigilante_2hora),
                str(asignacion.vigilante_final),
                asignacion.dia_reunion
            ))
            return cursor.lastrowid
    
    def obtener_todas(self) -> List[tuple]:
        """Obtiene todas las asignaciones como tuplas"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT semana, acomodadores_1hora, acomodadores_2hora, 
                       acomodador_final, vigilante_1hora, vigilante_2hora,
                       vigilante_final, dia_reunion
                FROM asignaciones
                ORDER BY id
            """)
            return cursor.fetchall()
    
    def obtener_por_mes(self, numero_mes: int) -> List[tuple]:
        """Obtiene asignaciones de un mes específico"""
        with sqlite3.connect(self.db_path) as conn:
            # Buscar semanas que contengan el nombre del mes
            meses = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio",
                    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
            mes_nombre = meses[numero_mes]
            
            cursor = conn.execute("""
                SELECT semana, acomodadores_1hora, acomodadores_2hora,
                       acomodador_final, vigilante_1hora, vigilante_2hora,
                       vigilante_final, dia_reunion
                FROM asignaciones
                WHERE LOWER(semana) LIKE ?
                ORDER BY id
            """, (f"%{mes_nombre}%",))
            return cursor.fetchall()
    
    def eliminar_todas(self):
        """Elimina todas las asignaciones"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM asignaciones")
    
    def actualizar(self, id_asignacion: int, columna: str, valor: str):
        """Actualiza una columna específica de una asignación"""
        columnas_validas = [
            'acomodadores_1hora', 'acomodadores_2hora', 'acomodador_final',
            'vigilante_1hora', 'vigilante_2hora', 'vigilante_final', 'dia_reunion'
        ]
        
        if columna not in columnas_validas:
            raise ValueError(f"Columna '{columna}' no es válida")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                f"UPDATE asignaciones SET {columna} = ? WHERE id = ?",
                (valor, id_asignacion)
            )