import tkinter as tk
from src.ui.components.vigilancia_panel import VigilanciaPanel
from src.ui.components.acomodador_panel import AcomodadoresPanel

def on_vigilantes_seleccionados(seleccionados):
    print(f"Vigilantes seleccionados: {[str(v) for v in seleccionados]}")

root = tk.Tk()
root.title("Sistema de Asignaciones")
root.geometry("800x600")

# Crear frame para ambos paneles
frame_principal = tk.Frame(root)
frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Panel de acomodadores (columna 0)
panel_acomodadores = AcomodadoresPanel(frame_principal)
panel_acomodadores.grid(row=0, column=0, sticky="nsew", padx=5)

# Panel de vigilancia (columna 1)
panel_vigilancia = VigilanciaPanel(
    frame_principal,
    on_seleccion_callback=on_vigilantes_seleccionados
)
panel_vigilancia.grid(row=0, column=1, sticky="nsew", padx=5)

# Configurar expansión
frame_principal.grid_columnconfigure(0, weight=1)
frame_principal.grid_columnconfigure(1, weight=1)
frame_principal.grid_rowconfigure(0, weight=1)

# Ejemplo: Establecer grupo de limpieza (semana 3 = grupo 3)
# panel_vigilancia.set_grupo_limpieza(3)

root.mainloop()