import tkinter as tk
from tkinter import messagebox, Listbox, END, Menu
from typing import Callable, List, Optional
from src.models.persona import Persona
from src.services.vigilancia_service import VigilanciaService
from src.config.constants import COLORES, FUENTES

class VigilanciaPanel(tk.Frame):
    """
    Componente UI para gestionar vigilancia
    Incluye sistema de grupos y menú contextual
    """
    
    def __init__(self, parent, service: VigilanciaService = None,
                 on_seleccion_callback: Callable = None,
                 numero_grupo_limpieza: Optional[int] = None):
        super().__init__(parent)
        self.service = service or VigilanciaService()
        self.on_seleccion_callback = on_seleccion_callback
        self.numero_grupo_limpieza = numero_grupo_limpieza
        self.vigilantes_actuales: List[Persona] = []
        
        self._configurar_estilos()
        self._crear_widgets()
        self._crear_menu_contextual()
        self._cargar_datos_iniciales()
    
    def _configurar_estilos(self):
        """Configura los estilos del panel"""
        self.config(bg=COLORES['fondo_oscuro'])
    
    def _crear_widgets(self):
        """Crea todos los widgets del panel"""
        # Título
        self.titulo = tk.Label(
            self,
            text="Vigilancia",
            fg=COLORES['texto_claro'],
            bg=COLORES['fondo_titulo'],
            font=FUENTES['titulo'],
            relief="solid"
        )
        self.titulo.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Frame info de grupos
        self.frame_info = tk.Frame(self, bg=COLORES['fondo_oscuro'])
        self.frame_info.grid(row=1, column=0, sticky="ew", padx=5)
        
        self.label_grupo = tk.Label(
            self.frame_info,
            text="Todos los vigilantes",
            fg=COLORES['texto_claro'],
            bg=COLORES['fondo_oscuro'],
            font=FUENTES['listbox']
        )
        self.label_grupo.pack()
        
        # Listbox con scrollbar
        frame_list = tk.Frame(self, bg=COLORES['fondo_oscuro'])
        frame_list.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(frame_list)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = Listbox(
            frame_list,
            relief="raised",
            font=FUENTES['listbox'],
            fg=COLORES['texto_claro'],
            bg=COLORES['fondo_listbox'],
            yscrollcommand=scrollbar.set
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # Bind para menú contextual
        self.listbox.bind("<Button-3>", self._mostrar_menu_contextual)
        
        # Frame de botones
        frame_botones = tk.Frame(self, bg=COLORES['fondo_oscuro'])
        frame_botones.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        
        self._crear_botones(frame_botones)
        
        # Configurar expansión
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
    
    def _crear_botones(self, parent):
        """Crea los botones de acción"""
        botones_config = [
            ("Remover", self._on_remover_click),
            ("Selección aleatoria", self._on_aleatorio_click),
            ("Reiniciar", self._on_reiniciar_click),
            ("Ver grupos", self._on_ver_grupos_click)
        ]
        
        for texto, comando in botones_config:
            btn = tk.Button(
                parent,
                text=texto,
                command=comando,
                relief="groove",
                bg=COLORES['boton'],
                fg=COLORES['texto_boton'],
                activebackground=COLORES['boton_hover']
            )
            btn.pack(side=tk.TOP, fill=tk.X, pady=2)
    
    def _crear_menu_contextual(self):
        """Crea el menú contextual (click derecho)"""
        self.menu_contextual = Menu(self, tearoff=0)
        self.menu_contextual.add_command(
            label="Remover seleccionado",
            command=self._on_remover_click
        )
        self.menu_contextual.add_command(
            label="Ver grupo",
            command=self._ver_grupo_de_seleccionado
        )
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(
            label="Estadísticas de grupos",
            command=self._on_ver_grupos_click
        )
    
    def _mostrar_menu_contextual(self, event):
        """Muestra el menú contextual"""
        try:
            self.listbox.selection_clear(0, END)
            self.listbox.selection_set(self.listbox.nearest(event.y))
            self.menu_contextual.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_contextual.grab_release()
    
    def _cargar_datos_iniciales(self):
        """Carga los vigilantes iniciales"""
        self.actualizar_lista()
    
    def actualizar_lista(self, filtrar_por_grupo: int = None):
        """
        Actualiza la lista de vigilantes desde la BD
        Args:
            filtrar_por_grupo: Si se especifica, muestra solo ese grupo
        """
        self.listbox.delete(0, END)
        
        if filtrar_por_grupo:
            grupo = self.service.obtener_grupo_por_numero(filtrar_por_grupo)
            self.vigilantes_actuales = grupo.miembros if grupo else []
            self.label_grupo.config(text=f"Grupo {filtrar_por_grupo} de limpieza")
        else:
            self.vigilantes_actuales = self.service.obtener_vigilantes_activos()
            self.label_grupo.config(text="Todos los vigilantes")
        
        for persona in self.vigilantes_actuales:
            num_grupo = self.service.obtener_grupo_de_persona(persona)
            self.listbox.insert(END, f"{persona} (Grupo {num_grupo})")
    
    def set_grupo_limpieza(self, numero_grupo: int):
        """Establece el grupo de limpieza y filtra la lista"""
        self.numero_grupo_limpieza = numero_grupo
        self.actualizar_lista(numero_grupo)
    
    def _on_remover_click(self):
        """Maneja el click en remover"""
        seleccion = self.listbox.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un vigilante")
            return
        
        indice = seleccion[0]
        persona = self.vigilantes_actuales[indice]
        
        respuesta = messagebox.askyesno(
            "Confirmar",
            f"¿Desea remover a {persona} del grupo {self.service.obtener_grupo_de_persona(persona)}?"
        )
        
        if respuesta:
            try:
                self.service.remover_vigilante_de_grupo(persona.id)
                self.actualizar_lista()
                messagebox.showinfo("Éxito", f"{persona} ha sido removido")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo remover: {e}")
    
    def _on_aleatorio_click(self):
        """Maneja el click en selección aleatoria"""
        try:
            es_valido, mensaje = self.service.validar_cantidad_minima(3)
            if not es_valido:
                messagebox.showerror("Error", mensaje)
                return
            
            # Si hay grupo de limpieza, seleccionar de ese grupo
            if self.numero_grupo_limpieza:
                seleccionados, mensaje_formato = self.service.seleccionar_por_grupo(
                    self.numero_grupo_limpieza
                )
            else:
                seleccionados, mensaje_formato = self.service.seleccionar_aleatorios(3)
            
            messagebox.showinfo("Seleccionados", mensaje_formato)
            
            if self.on_seleccion_callback:
                self.on_seleccion_callback(seleccionados)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error en la selección: {e}")
    
    def _on_reiniciar_click(self):
        """Maneja el click en reiniciar"""
        respuesta = messagebox.askyesno(
            "Confirmar",
            "¿Desea reactivar todos los vigilantes?"
        )
        
        if respuesta:
            try:
                self.service.reiniciar_todos()
                self.actualizar_lista()
                messagebox.showinfo("Éxito", "Todos los vigilantes han sido reactivados")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo reiniciar: {e}")
    
    def _on_ver_grupos_click(self):
        """Muestra las estadísticas de todos los grupos"""
        stats = self.service.obtener_estadisticas_grupos()
        
        mensaje = "ESTADÍSTICAS DE GRUPOS DE VIGILANCIA\n\n"
        for num in sorted(stats.keys()):
            info = stats[num]
            mensaje += f"Grupo {num}: {info['cantidad_activos']} activos\n"
            for nombre in info['activos']:
                mensaje += f"  • {nombre}\n"
            mensaje += "\n"
        
        # Crear ventana con texto scrollable
        ventana = tk.Toplevel(self)
        ventana.title("Grupos de Vigilancia")
        ventana.geometry("400x500")
        
        text = tk.Text(ventana, wrap=tk.WORD, font=FUENTES['listbox'])
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert("1.0", mensaje)
        text.config(state=tk.DISABLED)
    
    def _ver_grupo_de_seleccionado(self):
        """Muestra el grupo del vigilante seleccionado"""
        seleccion = self.listbox.curselection()
        if not seleccion:
            return
        
        persona = self.vigilantes_actuales[seleccion[0]]
        num_grupo = self.service.obtener_grupo_de_persona(persona)
        
        if num_grupo > 0:
            messagebox.showinfo(
                "Grupo",
                f"{persona} pertenece al Grupo {num_grupo}"
            )
    
    def obtener_seleccionados(self) -> List[Persona]:
        """Obtiene los vigilantes actualmente en la lista"""
        return self.vigilantes_actuales
    
    def aplicar_tema(self, tema: str):
        """Aplica un tema (claro/oscuro)"""
        if tema == "oscuro":
            self.config(bg=COLORES['fondo_oscuro'])
            self.listbox.config(
                fg=COLORES['texto_claro'],
                bg=COLORES['fondo_listbox']
            )
        else:
            self.config(bg="#F5F5F5")
            self.listbox.config(fg="#000000", bg="#FFFFFF")