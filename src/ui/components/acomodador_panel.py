import tkinter as tk
from tkinter import messagebox, Listbox, END
from typing import Callable, List
from src.models.persona import Persona
from src.services.acomodador_service import AcomodadorService
from src.config.constants import COLORES, FUENTES

class AcomodadoresPanel(tk.Frame):
    """Componente UI para gestionar acomodadores - Patrón MVC/Observer"""
    

    def __init__(self, parent, service: AcomodadorService = None, 
                 on_seleccion_callback: Callable = None):
        super().__init__(parent)
        self.service = service or AcomodadorService()
        self.on_seleccion_callback = on_seleccion_callback
        self.acomodadores_actuales: List[Persona] = []
        
        self._configurar_estilos()
        self._crear_widgets()
        self._cargar_datos_iniciales()
    
    def _configurar_estilos(self):
        """Configura los estilos del panel"""
        self.config(bg=COLORES['fondo_oscuro'])
    
    def _crear_widgets(self):
        """Crea todos los widgets del panel"""
        # Título
        self.titulo = tk.Label(
            self,
            text="Acomodadores",
            fg=COLORES['texto_claro'],
            bg=COLORES['fondo_titulo'],
            font=FUENTES['titulo'],
            relief="solid"
        )
        self.titulo.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Listbox
        self.listbox = Listbox(
            self,
            relief="raised",
            font=FUENTES['listbox'],
            fg=COLORES['texto_claro'],
            bg=COLORES['fondo_listbox']
        )
        self.listbox.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Frame de botones
        frame_botones = tk.Frame(self, bg=COLORES['fondo_oscuro'])
        frame_botones.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        
        # Botones
        self._crear_botones(frame_botones)
        
        # Configurar expansión
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
    
    def _crear_botones(self, parent):
        """Crea los botones de acción"""
        botones_config = [
            ("Remover", self._on_remover_click),
            ("Selección aleatoria", self._on_aleatorio_click),
            ("Reiniciar", self._on_reiniciar_click)
        ]
        
        for i, (texto, comando) in enumerate(botones_config):
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
    
    def _cargar_datos_iniciales(self):
        """Carga los acomodadores iniciales"""
        self.actualizar_lista()
    
    def actualizar_lista(self):
        """Actualiza la lista de acomodadores desde la BD"""
        self.listbox.delete(0, END)
        self.acomodadores_actuales = self.service.obtener_acomodadores_activos()
        
        for persona in self.acomodadores_actuales:
            self.listbox.insert(END, str(persona))
    
    def _on_remover_click(self):
        """Maneja el click en remover"""
        seleccion = self.listbox.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un acomodador")
            return
        
        indice = seleccion[0]
        persona = self.acomodadores_actuales[indice]
        
        # Confirmar
        respuesta = messagebox.askyesno(
            "Confirmar",
            f"¿Desea remover a {persona}?"
        )
        
        if respuesta:
            try:
                self.service.desactivar_acomodador(persona.id)
                self.actualizar_lista()
                messagebox.showinfo("Éxito", f"{persona} ha sido removido")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo remover: {e}")
    
    def _on_aleatorio_click(self):
        """Maneja el click en selección aleatoria"""
        try:
            # Validar cantidad mínima
            es_valido, mensaje = self.service.validar_cantidad_minima(5)
            if not es_valido:
                messagebox.showerror("Error", mensaje)
                return
            
            # Seleccionar
            seleccionados, mensaje_formato = self.service.seleccionar_aleatorios(5)
            
            # Mostrar resultado
            messagebox.showinfo("Seleccionados", mensaje_formato)
            
            # Notificar al callback si existe
            if self.on_seleccion_callback:
                self.on_seleccion_callback(seleccionados)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error en la selección: {e}")
    
    def _on_reiniciar_click(self):
        """Maneja el click en reiniciar"""
        respuesta = messagebox.askyesno(
            "Confirmar",
            "¿Desea reactivar todos los acomodadores?"
        )
        
        if respuesta:
            try:
                self.service.reiniciar_todos()
                self.actualizar_lista()
                messagebox.showinfo("Éxito", "Todos los acomodadores han sido reactivados")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo reiniciar: {e}")
    
    def obtener_seleccionados(self) -> List[Persona]:
        """Obtiene los acomodadores actualmente seleccionados"""
        return self.acomodadores_actuales
    
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
