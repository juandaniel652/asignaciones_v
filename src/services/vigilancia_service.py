import random
from typing import List, Tuple, Dict
from src.models.persona import Persona, TipoPersona
from src.models.grupo_vigilancia import GrupoVigilancia
from src.database.repositories.persona_repository import PersonaRepository

class VigilanciaService:
    """Servicio para gestionar la vigilancia con sistema de grupos"""
    
    def __init__(self, repository: PersonaRepository = None):
        self.repository = repository or PersonaRepository()
        self._inicializar_grupos()
    
    def _inicializar_grupos(self):
        """
        Inicializa los 6 grupos de vigilancia predefinidos
        Estos grupos rotan para mantener equidad
        """
        # Nombres completos según tu lista original
        self.grupos_config = {
            1: ["Ferreira Rocio", "Gomez Yanina", "Israelson Analia", "Valiente Silvia"],
            2: ["Coronel Vanesa", "Dominguez Alejandra", "Quiroz Rosario"],
            3: ["Altamirano Maia", "Altamirano Pamela", "Cardozo Karolaine", "Gonzalez Iris"],
            4: ["Carena Graciela", "Deiana Ruth", "Valiente Fátima"],
            5: ["Dominguez Miriam", "Encina Mónica", "Viera Valeria"],
            6: ["Arguello Monica", "Benitez Gabriela", "Ledesma Susana", "Sotelo Rosa"]
        }
    
    def obtener_vigilantes_activos(self) -> List[Persona]:
        """Obtiene todos los vigilantes activos ordenados"""
        return self.repository.obtener_todos(TipoPersona.VIGILANTE)
    
    def obtener_grupos(self) -> Dict[int, GrupoVigilancia]:
        """
        Obtiene los grupos de vigilancia con sus miembros actuales
        Returns: Dict con número de grupo y objeto GrupoVigilancia
        """
        vigilantes = self.obtener_vigilantes_activos()
        grupos = {}
        
        for num_grupo, nombres in self.grupos_config.items():
            miembros = [v for v in vigilantes if str(v) in nombres]
            grupos[num_grupo] = GrupoVigilancia(num_grupo, miembros)
        
        return grupos
    
    def obtener_grupo_por_numero(self, numero: int) -> GrupoVigilancia:
        """Obtiene un grupo específico por su número"""
        grupos = self.obtener_grupos()
        return grupos.get(numero)
    
    def obtener_grupo_de_persona(self, persona: Persona) -> int:
        """Encuentra a qué grupo pertenece una persona"""
        grupos = self.obtener_grupos()
        for num, grupo in grupos.items():
            if grupo.contiene_persona(persona):
                return num
        return 0  # No pertenece a ningún grupo
    
    def seleccionar_aleatorios(self, cantidad: int = 3, 
                              excluir_grupo: int = None) -> Tuple[List[Persona], str]:
        """
        Selecciona vigilantes aleatoriamente
        Args:
            cantidad: Cantidad a seleccionar (default 3)
            excluir_grupo: Número de grupo a excluir (opcional)
        Returns: (lista_seleccionados, mensaje_formateado)
        """
        vigilantes = self.obtener_vigilantes_activos()
        
        # Filtrar si se debe excluir un grupo
        if excluir_grupo:
            grupo_excluido = self.obtener_grupo_por_numero(excluir_grupo)
            vigilantes = [v for v in vigilantes 
                         if v not in grupo_excluido.miembros]
        
        if len(vigilantes) < cantidad:
            raise ValueError(
                f"Se necesitan al menos {cantidad} vigilantes activos. "
                f"Actualmente hay {len(vigilantes)}."
            )
        
        seleccionados = random.sample(vigilantes, cantidad)
        mensaje = self._formatear_seleccion(seleccionados)
        
        return seleccionados, mensaje
    
    def seleccionar_por_grupo(self, numero_grupo: int) -> Tuple[List[Persona], str]:
        """
        Selecciona vigilantes de un grupo específico
        Útil para rotación de grupos de limpieza
        """
        grupo = self.obtener_grupo_por_numero(numero_grupo)
        
        if not grupo or len(grupo.miembros) < 3:
            raise ValueError(
                f"El grupo {numero_grupo} no tiene suficientes miembros activos"
            )
        
        # Tomar hasta 3 personas del grupo
        seleccionados = grupo.miembros[:3]
        mensaje = self._formatear_seleccion(seleccionados)
        
        return seleccionados, mensaje
    
    def _formatear_seleccion(self, seleccionados: List[Persona]) -> str:
        """Formatea la selección para mostrar"""
        if len(seleccionados) < 3:
            return "Selección incompleta"
        
        return (
            f"Vigilancia 1° hora: {seleccionados[0]}\n\n"
            f"Vigilancia 2° hora: {seleccionados[1]}\n\n"
            f"Vigilancia después de la reunión: {seleccionados[2]}"
        )
    
    def remover_vigilante_de_grupo(self, persona_id: int, 
                                   actualizar_lista: bool = True):
        """
        Remueve un vigilante (lo desactiva)
        Args:
            persona_id: ID de la persona
            actualizar_lista: Si debe actualizar la lista después
        """
        self.repository.desactivar(persona_id)
    
    def reiniciar_todos(self) -> List[Persona]:
        """Reactiva todos los vigilantes"""
        import sqlite3
        with sqlite3.connect(self.repository.db_path) as conn:
            cursor = conn.execute(
                "SELECT id FROM personas WHERE tipo = ?",
                (TipoPersona.VIGILANTE.value,)
            )
            for row in cursor.fetchall():
                self.repository.activar(row[0])
        
        return self.obtener_vigilantes_activos()
    
    def agregar_vigilante(self, nombre: str, apellido: str, 
                         numero_grupo: int = None) -> Persona:
        """Agrega un nuevo vigilante a un grupo específico"""
        persona = Persona(
            nombre=nombre,
            apellido=apellido,
            tipo=TipoPersona.VIGILANTE,
            activo=True,
            grupo=numero_grupo
        )
        persona.id = self.repository.agregar(persona)
        return persona
    
    def validar_cantidad_minima(self, minimo: int = 3) -> Tuple[bool, str]:
        """Valida que haya suficientes vigilantes activos"""
        activos = self.obtener_vigilantes_activos()
        es_valido = len(activos) >= minimo
        mensaje = f"Hay {len(activos)} vigilantes activos. Se necesitan al menos {minimo}."
        return es_valido, mensaje
    
    def obtener_estadisticas_grupos(self) -> Dict[int, Dict]:
        """
        Obtiene estadísticas de cada grupo
        Returns: Dict con info de cada grupo (número, cantidad activos, nombres)
        """
        grupos = self.obtener_grupos()
        stats = {}
        
        for num, grupo in grupos.items():
            stats[num] = {
                'numero': num,
                'total': len(grupo.miembros),
                'activos': [str(p) for p in grupo.miembros if p.activo],
                'cantidad_activos': len([p for p in grupo.miembros if p.activo])
            }
        
        return stats