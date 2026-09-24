# Módulo src — funciones reutilizables del proyecto
# Importaciones principales para facilitar el acceso desde los notebooks.

from .carga import cargar_csv_raw, cargar_todos_los_raw
from .transformacion import (
    normalizar_mes,
    construir_ds,
    aplicar_regla_carnet,
    agregar_regimen,
    construir_panel_mensual,
)

__all__ = [
    "cargar_csv_raw",
    "cargar_todos_los_raw",
    "normalizar_mes",
    "construir_ds",
    "aplicar_regla_carnet",
    "agregar_regimen",
    "construir_panel_mensual",
]
