# Decisiones de Modelado — Prophet
## Proyecto: Predicción de Demanda de Trámites Migratorios — Perú

**Versión:** 1.0 · **Fecha:** 2026-09-24 · **Estado:** Acordado (Fase 3 completada)

> Este documento se actualiza solo por decisión explícita de ambos integrantes del equipo.
> Sirve como referencia fija para implementar los modelos en la Fase 4.

---

## Tabla de decisiones por tipo de trámite

| Parámetro | `prorroga_residencia` | `cambio_calidad` | `carnet_extranjeria` | `solicitud_visas` |
|---|---|---|---|---|
| **Datos de entrada** | Panel completo (20 meses, ene-2025 a ago-2026) | Solo `regimen = post_2026` (8 meses: ene–ago 2026) | 19 meses (ene-2025 a jul-2026, excl. ago-2026 por subreporte) | Panel completo (20 meses, ene-2025 a ago-2026) |
| **`yearly_seasonality`** | `True` | `False` | Pendiente de evaluar (\*) | Pendiente de evaluar (\*) |
| **Granularidad del modelo** | Por sede (mínimo top-5: Lima, Trujillo, Arequipa, Piura, Chiclayo) | Nacional agregado (por ahora) | Nacional agregado (por ahora) | Nacional agregado |
| **Regresor externo** | Ninguno | Ninguno | Ninguno | Ninguno (ver nota \*\*) |
| **Horizonte de pronóstico** | 6 meses | 6 meses | 6 meses | 6 meses |
| **Columna `regimen`** | No aplica | Separar en dos series; modelar solo `post_2026` | No aplica (no separar; quiebre es artefactual) | No aplica |

---

## Justificación de cada decisión

### Prórroga de Residencia

- **Datos completos (20 meses):** No tiene quiebre estructural confirmado entre 2025 y 2026.
  La serie es homogénea y el nivel es estable.
- **`yearly_seasonality=True`:** Confirmado en Análisis A del EDA (Fase 3). El pico de enero
  es sistémico en **todas las sedes** (ratios Ene/Promedio entre 1.41x y 1.90x). Con 20 meses
  (casi 2 ciclos anuales), Prophet puede estimar la estacionalidad anual con confianza razonable.
- **Modelo por sede:** Cada sede tiene suficiente volumen y señal estacional propia para un
  modelo individual. Lima concentra el 77.8% del volumen, pero las sedes regionales también
  son modelables.

### Cambio de Calidad Migratoria

- **Solo `post_2026` (8 meses):** Quiebre estructural severo confirmado en Análisis C del EDA.
  La caída dic-2025 → ene-2026 fue del **−51.7%** y el nuevo nivel promedio (5,867) representa
  solo el 61.5% del promedio 2025 (9,546). Excluir agosto 2026 no altera esta caída (−38.3% en 7m),
  lo que confirma que el quiebre es estructural y normativo, no un problema de reporte.
  Incluir datos pre-2026 sesgaría el modelo con un nivel de demanda que ya no existe.
- **`yearly_seasonality=False`:** Con solo 8 meses de datos en el período `post_2026`, Prophet
  no tiene información suficiente para estimar una estacionalidad anual confiable.
- **Nacional agregado:** Con 8 meses de historia, la desagregación por sede reduciría aún
  más los datos disponibles por serie. Se inicia con el modelo nacional.

### Carné de Extranjería (neto, Regla 1 ya aplicada)

- **19 meses de historia (ene-2025 a jul-2026, excluyendo ago-2026):**
  El análisis extendido (C.2) demostró que el supuesto "quiebre estructural" en Carné es en gran
  medida un **artefacto de rezago de reporte**:
  1. En enero de 2026 la serie no cayó, sino que subió (+4.5% vs dic-2025: 7,608 → 7,949 trámites).
  2. La caída en el promedio anual 2026 está concentrada en los meses finales, especialmente
     agosto-2026 (caída de −15.9% vs julio), debido al tiempo administrativo que toma la emisión y
     entrega física del documento tras el otorgamiento del cambio de calidad.
  3. Al excluir agosto-2026, la diferencia promedio vs 2025 baja a solo **−5.3%** (7,080 vs 7,477);
     y excluyendo julio y agosto baja a **−4.0%** (7,179). Esta variación está dentro del rango normal
     de fluctuación mensual y no justifica descartar 12 meses valiosos de historia.
  4. **Decisión:** Mantener 19 meses continuos (descartando únicamente agosto-2026 por incompleto) y
     **no separar por régimen**.
- **`yearly_seasonality` — Pendiente de evaluar (\*):**
  Al conservar 19 meses continuos, se dispone de masa crítica suficiente para probar empíricamente
  `yearly_seasonality=True` vs `yearly_seasonality=False` mediante validación cruzada en la Fase 4,
  en lugar de forzarlo a `False`.
- **Nacional agregado:** Al no fragmentar la serie por régimen, se preserva mayor robustez para el
  ajuste nacional antes de considerar aperturas por sede.

### Solicitud de Calidad Migratoria (Visas)

- **Datos completos (20 meses):** Serie sin quiebre estructural. Nivel relativamente estable
  durante todo el período.
- **`yearly_seasonality` — Pendiente (\*):** El Análisis B del EDA mostró que `solicitud_visas`
  no tiene estacionariedad ADF robusta en niveles ni en primeras diferencias (p=0.052).
  En Fase 4 se probará con `yearly_seasonality=True` y `False`, comparando los errores
  de validación cruzada, antes de decidir.
- **Nacional agregado:** El volumen total es pequeño (23,905 trámites en 20 meses) y Lima
  concentra el 93.5% del volumen. No tiene sentido modelar por sede.

---

## Notas adicionales

**(\*) `yearly_seasonality` de `solicitud_visas`:**
Se evaluará en Fase 4 mediante `prophet.diagnostics.cross_validation()` con horizontes
de 1 a 3 meses. La versión que minimice el MAPE en el set de validación será la elegida.

**(\*\*) Regresor externo (Granger):**
El test de Granger en Análisis B del EDA mostró una señal marginalmente significativa
(F-test p=0.024 en lag 2) para `visas → cambio_calidad`, pero la muestra es demasiado
pequeña (19 obs.) para ser concluyente. **Decisión: no incorporar regresor externo en
Fase 4.** Revisión programada cuando haya ≥ 24 meses de datos (`post_2026`).

---

## Referencias cruzadas

| Documento | Contenido |
|---|---|
| `notebooks/03_eda_avanzado.ipynb` | Análisis A, B, C que sustentan estas decisiones |
| `reports/issues_fase3.md` | Issues de GitHub derivados del EDA |
| `data/processed/panel_unificado.csv` | Fuente de datos del modelado |
| `docs/fuentes_datos.md` | Origen y descripción de los datos raw |
