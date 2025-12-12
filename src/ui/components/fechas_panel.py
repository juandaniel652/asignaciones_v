import tkinter as tk
from tkinter import Listbox, Text, messagebox, END
from typing import Callable, List, Optional
from src.models.semana import Semana
from src.services.fecha_service import FechaService
from src.config.constants import COLORES, FUENTES

class FechasPanel(tk.Frame):
    """Panel para gestión de fechas y semanas"""
    
    def __init__(self, parent, service: FechaService = None,
                 on_seleccion_callback: Callable = None):
        super().__init__(parent)
        self.service = service or FechaService()
        self.on_seleccion_callback = on_seleccion_callback
        self.semanas: List[Semana] = []
        self.semana_seleccionada: Optional[Semana] = None
        
        self._configurar_estilos()
        self._crear_widgets()
        self._cargar_datos_iniciales()
    
    def _configurar_estilos(self):
        self.config(bg=COLORES['fondo_oscuro'])
    
    def _crear_widgets(self):
        # Título
        titulo = tk.Label(
            self,
            text="Semanas",
            fg=COLORES['texto_claro'],
            bg=COLORES['fondo_titulo'],
            font=FUENTES['titulo'],
            relief="solid"
        )
        titulo.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Listbox de semanas
        frame_list = tk.Frame(self, bg=COLORES['fondo_oscuro'])
        frame_list.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(frame_list)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = Listbox(
            frame_list,
            relief="raised",
            font=FUENTES['listbox'],
            fg=COLORES['texto_claro'],
            bg=COLORES['fondo_listbox'],
            width=30,
            yscrollcommand=scrollbar.set
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # Botón mostrar
        btn_mostrar = tk.Button(
            self,
            text="Mostrar",
            command=self._on_mostrar_click,
            relief="groove",
            bg=COLORES['boton'],
            fg=COLORES['texto_boton']
        )
        btn_mostrar.grid(row=2, column=0, sticky="ew", padx=5, pady=2)
        
        # Configurar expansión
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
    
    def _cargar_datos_iniciales(self):
        """Carga las semanas"""
        self.semanas = self.service.generar_semanas(cantidad=52)
        self._actualizar_listbox()
    
    def _actualizar_listbox(self):
        """Actualiza el listbox con las semanas"""
        self.listbox.delete(0, END)
        textos = self.service.formatear_para_listbox(self.semanas)
        
        for texto in textos:
            self.listbox.insert(END, texto)
    
    def _on_mostrar_click(self):
        """Maneja el click en mostrar"""
        seleccion = self.listbox.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una semana")
            return
        
        indice = seleccion[0]
        self.semana_seleccionada = self.semanas[indice]
        
        # Mostrar información
        messagebox.showinfo(
            "Semana Seleccionada",
            f"{self.semana_seleccionada}\n\n"
            f"Grupo de limpieza: {self.semana_seleccionada.grupo_limpieza}"
        )
        
        # Notificar callback
        if self.on_seleccion_callback:
            self.on_seleccion_callback(self.semana_seleccionada)
    
    def obtener_semana_seleccionada(self) -> Optional[Semana]:
        """Obtiene la semana actualmente seleccionada"""
        return self.semana_seleccionada
    
    def obtener_todas_semanas(self) -> List[Semana]:
        """Obtiene todas las semanas cargadas"""
        return self.semanas