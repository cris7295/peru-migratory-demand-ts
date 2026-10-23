# Notebooks

Ejecutar en orden, desde la raíz del proyecto o la carpeta notebooks:

1. `01_exploracion_datos.ipynb`: carga estricta, cobertura y composición de originales.
2. `02_panel_unificado.ipynb`: panel histórico y componentes de carné, con reconciliación.
3. `03_eda_avanzado.ipynb`: estacionalidad por año, pruebas exploratorias y referencias predictivas.

La fase 4 aún no está implementada. Los notebooks no declaran un ganador Prophet.
Los cálculos reutilizables viven en `src/`; `python -m src.auditoria` exporta la evidencia.
