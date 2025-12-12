import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, List, Optional, Dict
from src.models.asignacion import Asignacion
from src.models.persona import Persona
from src.services.asignacion_service import AsignacionService
from src.services.acomodador_service import AcomodadorService
from src.services.vigilancia_service import VigilanciaService

class AsignacionesTable(ttk.Treeview):
    """
    TreeView especializado para mostrar y editar asignaciones
    Componente reutilizable con edición in-place
    """
    
    # Definición de columnas
    COLUMNAS = {
        'semana': {'texto': 'Semanas', 'ancho': 173, 'editable': False},
        'acomo_1h': {'texto': 'Acomodadores 1° hora', 'ancho': 220, 'editable': True},
        'acomo_2h': {'texto': 'Acomodadores 2° hora', 'ancho': 220, 'editable': True},
        'acomo_final': {'texto': 'Acomodador final', 'ancho': 145, 'editable': True},
        'vigil_1h': {'texto': 'Vigilancia 1° hora', 'ancho': 145, 'editable': True},
        'vigil_2h': {'texto': 'Vigilancia 2° hora', 'ancho': 145, 'editable': True},
        'vigil_final': {'texto': 'Vigilancia final', 'ancho': 145, 'editable': True},
        'dia_reunion': {'texto': 'Días de reunión', 'ancho': 173, 'editable': False}
    }
    
    def __init__(self, parent, 
                 asignacion_service: AsignacionService = None,
                 acomodador_service: AcomodadorService = None,
                 vigilancia_service: VigilanciaService = None):
        
        # Configurar columnas
        columnas = list(self.COLUMNAS.keys())
        super().__init__(parent, columns=columnas, show='headings')
        
        self.asignacion_service = asignacion_service or AsignacionService()
        self.acomodador_service = acomodador_service or AcomodadorService()
        self.vigilancia_service = vigilancia_service or VigilanciaService()
        
        self._configurar_columnas()
        self._aplicar_estilos()
        self._configurar_eventos()
    
    def _configurar_columnas(self):
        """Configura encabezados y anchos de columnas"""
        for col_id, config in self.COLUMNAS.items():
            self.heading(col_id, text=config['texto'])
            self.column(col_id, width=config['ancho'], minwidth=config['ancho'])
    
    def _aplicar_estilos(self):
        """Aplica estilos modernos al TreeView"""
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview",
                       background="#2b2b2b",
                       foreground="white",
                       rowheight=25,
                       fieldbackground="#2b2b2b",
                       font=("Segoe UI", 10))
        
        style.configure("Treeview.Heading",
                       background="#1f1f1f",
                       foreground="white",
                       font=("Segoe UI", 9, "bold"))
        
        style.map("Treeview",
                 background=[("selected", "#3a7ff6")],
                 foreground=[("selected", "white")])
    
    def _configurar_eventos(self):
        """Configura eventos de edición"""
        self.bind("<Double-1>", self._on_doble_click)
    
    def agregar_asignacion(self, asignacion: Asignacion) -> str:
        """
        Agrega una asignación al TreeView
        Returns: ID del item insertado
        """
        return self.insert("", "end", values=asignacion.to_tuple())
    
    def cargar_asignaciones(self, asignaciones: List[tuple]):
        """Carga múltiples asignaciones desde tuplas"""
        self.delete(*self.get_children())  # Limpiar
        
        for asignacion_tuple in asignaciones:
            self.insert("", "end", values=asignacion_tuple)
    
    def _on_doble_click(self, event):
        """Maneja el doble click para editar"""
        region = self.identify("region", event.x, event.y)
        if region != "cell":
            return
        
        # Identificar celda
        item_id = self.identify_row(event.y)
        column_id = self.identify_column(event.x)
        
        if not item_id or not column_id:
            return
        
        # Obtener índice de columna
        col_index = int(column_id.replace('#', '')) - 1
        col_name = list(self.COLUMNAS.keys())[col_index]
        
        # Verificar si es editable
        if not self.COLUMNAS[col_name]['editable']:
            messagebox.showwarning(
                "No Editable",
                "Esta columna no puede ser editada"
            )
            return
        
        # Preguntar modo de edición
        respuesta = messagebox.askquestion(
            "Modo de Edición",
            "¿Desea editar manualmente?\n\n"
            "Sí = Escribir texto\n"
            "No = Seleccionar de lista"
        )
        
        if respuesta == 'yes':
            self._editar_manual(item_id, col_index, col_name)
        else:
            self._editar_con_lista(item_id, col_index, col_name)
    
    def _editar_manual(self, item_id: str, col_index: int, col_name: str):
        """Edición manual con Entry"""
        # Obtener posición de la celda
        bbox = self.bbox(item_id, col_index)
        if not bbox:
            return
        
        x, y, width, height = bbox
        valor_actual = self.item(item_id, 'values')[col_index]
        
        # Crear Entry para edición
        entry = tk.Entry(self.master, width=width)
        entry.place(
            x=x + self.winfo_x(),
            y=y + self.winfo_y(),
            width=width,
            height=height
        )
        entry.insert(0, valor_actual)
        entry.focus()
        entry.select_range(0, tk.END)
        
        def guardar_cambios(event=None):
            nuevo_valor = entry.get()
            
            # Validar según el tipo de columna
            if self._validar_valor(col_name, nuevo_valor):
                valores = list(self.item(item_id, 'values'))
                valores[col_index] = nuevo_valor
                self.item(item_id, values=valores)
            else:
                messagebox.showerror(
                    "Error",
                    "El valor ingresado no es válido"
                )
            
            entry.destroy()
        
        entry.bind('<Return>', guardar_cambios)
        entry.bind('<Escape>', lambda e: entry.destroy())
        entry.bind('<FocusOut>', lambda e: entry.destroy())
    
    def _editar_con_lista(self, item_id: str, col_index: int, col_name: str):
        """Edición con Listbox de opciones"""
        # Determinar qué mostrar según la columna
        if 'acomo' in col_name:
            if col_name == 'acomo_final':
                # Un solo acomodador
                self._mostrar_selector_simple(
                    item_id, col_index,
                    self.acomodador_service.obtener_acomodadores_activos(),
                    "Seleccione un acomodador"
                )
            else:
                # Pareja de acomodadores
                self._mostrar_selector_pareja(
                    item_id, col_index,
                    self.acomodador_service.obtener_acomodadores_activos(),
                    "Seleccione 2 acomodadores"
                )
        
        elif 'vigil' in col_name:
            # Un vigilante
            self._mostrar_selector_simple(
                item_id, col_index,
                self.vigilancia_service.obtener_vigilantes_activos(),
                "Seleccione un vigilante"
            )
    
    def _mostrar_selector_simple(self, item_id: str, col_index: int,
                                 opciones: List[Persona], titulo: str):
        """Muestra un selector simple (una opción)"""
        ventana = tk.Toplevel(self.master)
        ventana.title(titulo)
        ventana.geometry("300x400")
        ventana.transient(self.master)
        ventana.grab_set()
        
        # Listbox
        listbox = tk.Listbox(ventana)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for persona in opciones:
            listbox.insert(tk.END, str(persona))
        
        def confirmar(event=None):
            seleccion = listbox.curselection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione una opción")
                return
            
            valor = listbox.get(seleccion[0])
            valores = list(self.item(item_id, 'values'))
            valores[col_index] = valor
            self.item(item_id, values=valores)
            ventana.destroy()
        
        listbox.bind('<Return>', confirmar)
        listbox.bind('<Double-1>', confirmar)
        
        btn = tk.Button(ventana, text="Confirmar", command=confirmar)
        btn.pack(pady=5)
    
    def _mostrar_selector_pareja(self, item_id: str, col_index: int,
                                opciones: List[Persona], titulo: str):
        """Muestra un selector de pareja (dos opciones)"""
        ventana = tk.Toplevel(self.master)
        ventana.title(titulo)
        ventana.geometry("300x400")
        ventana.transient(self.master)
        ventana.grab_set()
        
        tk.Label(ventana, text="Seleccione 2 personas (Ctrl + Click)").pack(pady=5)
        
        # Listbox con selección múltiple
        listbox = tk.Listbox(ventana, selectmode=tk.MULTIPLE)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for persona in opciones:
            listbox.insert(tk.END, str(persona))
        
        def confirmar():
            seleccion = listbox.curselection()
            if len(seleccion) != 2:
                messagebox.showwarning(
                    "Advertencia",
                    "Debe seleccionar exactamente 2 personas"
                )
                return
            
            persona1 = listbox.get(seleccion[0])
            persona2 = listbox.get(seleccion[1])
            valor = f"{persona1} / {persona2}"
            
            valores = list(self.item(item_id, 'values'))
            valores[col_index] = valor
            self.item(item_id, values=valores)
            ventana.destroy()
        
        btn = tk.Button(ventana, text="Confirmar", command=confirmar)
        btn.pack(pady=5)
    
    def _validar_valor(self, col_name: str, valor: str) -> bool:
        """Valida el valor según el tipo de columna"""
        if not valor:
            return False
        
        # Validaciones específicas
        if 'acomo_1h' in col_name or 'acomo_2h' in col_name:
            # Debe tener formato "Nombre1 / Nombre2"
            return ' / ' in valor
        
        return True
    
    def obtener_todas_filas(self) -> List[tuple]:
        """Obtiene todas las filas como tuplas"""
        filas = []
        for item_id in self.get_children():
            valores = self.item(item_id, 'values')
            filas.append(valores)
        return filas
    
    def limpiar(self):
        """Limpia todas las filas"""
        self.delete(*self.get_children())