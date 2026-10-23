# Datos procesados

- `panel_unificado.csv`: ds, y, tipo_tramite, sede, regimen. Conserva las cantidades
  del panel original. Desde la revisión 2026-10-23, regimen solo se aplica a cambio_calidad.
- `carnet_componentes.csv`: ds, sede, componente, y. Dos componentes disjuntos del
  dataset de carné: `otros_tramites` y `asociado_cambio_calidad`. Su suma recupera
  el total de carné original. `otros_tramites` coincide con carné en el panel histórico.

**No anexar o sumar ambas tablas.** Son vistas alternativas, no eventos adicionales.
La clasificación no confirma duplicados entre fuentes ni identifica personas únicas.
No se rellenan meses ausentes con cero. La madurez de agosto de 2026 no está confirmada.
Reconstrucción: ejecutar `notebooks/02_panel_unificado.ipynb` tras validar los ocho CSV.
