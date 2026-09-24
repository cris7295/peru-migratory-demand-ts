# Issues — Fase 3: EDA Avanzado y Validación de Hipótesis

Archivo de referencia para abrir los Issues en GitHub manualmente usando las plantillas
de `.github/ISSUE_TEMPLATE/`. Cada sección corresponde a un Issue.

---

## Issue 1 — Plantilla: `hallazgo.md`

**Título:** `[Hallazgo] Estacionalidad de Prórroga de Residencia es sistémica en toda la red de sedes`

---

### ¿Qué se encontró?

El pico de demanda en enero no es un efecto exclusivo de Lima: el mismo patrón
estacional (pico en enero, valle en septiembre) se repite en **todas las sedes del
top-5** (Lima, Trujillo, Arequipa, Piura y Chiclayo), con distintas intensidades.

Ratios `enero / promedio mensual` medidos sobre 2025:

| Sede | Enero | Promedio mensual | Ratio |
|---|---|---|---|
| Lima | 44,460 | 23,423 | **1.90x** |
| Trujillo | 2,812 | 1,514 | **1.86x** |
| Arequipa | 1,853 | 1,084 | **1.71x** |
| Piura | 964 | 635 | **1.52x** |
| Chiclayo | 865 | 613 | **1.41x** |

Ratio pico/valle (suma 2025+2026): entre **3.4x (Piura)** y **5.3x (Trujillo, Arequipa)**.

### ¿En qué dataset(s)?

`data/processed/panel_unificado.csv` — tipo_tramite: `prorroga_residencia`.
Análisis en `notebooks/03_eda_avanzado.ipynb`, Análisis A.

### ¿Cómo se confirmó?

1. Series indexadas (base=100 en enero) superpuestas por sede: misma forma de curva.
2. Test numérico: todas las sedes tienen `mes_pico = Enero` y ratio `Ene/Promedio > 1.3x`.
3. El patrón se mantiene tanto en 2025 (12 meses) como en los 8 meses de 2026.

### ¿Qué implica para el modelo o el proyecto?

- **`yearly_seasonality=True`** en Prophet para Prórroga de Residencia (confirmado).
- Es viable modelar por sede individualmente (cada sede tiene suficiente señal estacional).
- No es necesario crear un modelo separado para Lima vs. regiones — el mismo Prior de
  estacionalidad aplica a todas.

### ¿Queda alguna pregunta abierta?

- ¿La intensidad estacional de cada sede es estable año a año, o varía según flujos
  migratorios regionales? (Se podrá evaluar cuando haya datos de 2027.)

---

## Issue 2 — Plantilla: `pregunta_abierta.md`

**Título:** `[Pregunta] ¿Existe relación líder-rezago entre Solicitud de Visas y Cambio de Calidad Migratoria?`

---

### La pregunta

¿Puede usarse la serie de `solicitud_visas` como regresor externo en el modelo Prophet
de `cambio_calidad`, dado que las visas aprobadas anteceden en el tiempo a los cambios
de calidad migratoria?

### Por qué importa

Si existiera causalidad de Granger confirmada (visas → cambio en lag 1-2 meses),
podríamos incorporar las solicitudes de visas como señal predictiva adelantada en el
modelo, mejorando potencialmente la precisión del pronóstico.

### Opciones que estamos considerando

**Resultado actual del test (20 meses, primeras diferencias):**

| Dirección | Lag | F-test p | Resultado |
|---|---|---|---|
| visas → cambio_calidad | 1 | 0.8958 | No significativo |
| visas → cambio_calidad | 2 | **0.0240** | **Significativo** |
| cambio_calidad → visas | 1 | 0.6729 | No significativo |
| cambio_calidad → visas | 2 | 0.1525 | No significativo |

**Limitaciones importantes que frenan la conclusión:**
1. Muestra pequeña: 19 obs. tras diferenciación → baja potencia estadística.
2. `d(solicitud_visas)` es marginalmente no estacionaria (ADF p=0.052).
3. Solo el lag 2 del F-test es significativo; el lag 1 no lo es.

**Opciones:**
- A) No usar como regresor por ahora y revisar cuando haya ≥ 30 meses.
- B) Incorporarlo como regresor experimental y comparar MAPE con/sin en Fase 4.

**Decisión provisional (Fase 3):** Opción A — no usar. Revisar al completar 2026.

### Cómo se resolvería / qué información falta

- Esperar datos de sept-dic 2026 para tener al menos 24 meses y repetir el test.
- Con 24+ obs., el test de Granger tendrá potencia suficiente para un resultado concluyente.
- En paralelo, explorar correlación cruzada (CCF) como análisis exploratorio complementario.

---

## Issue 3 — Plantilla: `pregunta_abierta.md`

**Título:** `[Pregunta] ¿Cuál es la causa del quiebre estructural en Cambio de Calidad Migratoria (dic-2025 → ene-2026)?`

---

### La pregunta

La serie de `cambio_calidad` muestra una caída abrupta del **51.7%** entre
diciembre 2025 (12,168 trámites) y enero 2026 (5,872 trámites), manteniéndose
en un nivel promedio de 5,867 durante los 8 meses siguientes (vs. 9,546 en 2025).

¿Qué causó este quiebre estructural?

### Por qué importa

La causa determina si el nivel actual (2026) es:
- **Permanente** → modelar solo con datos 2026 (decisión actual), o
- **Transitorio** (ej. represamiento puntual) → podría recuperarse, lo que cambiaría
  la estrategia de modelado.

También afecta la confiabilidad de cualquier pronóstico: si no sabemos si el fenómeno
puede repetirse, el modelo tiene incertidumbre no cuantificable.

### Opciones que estamos considerando

Posibles explicaciones (ninguna confirmada todavía):

1. **Cambio normativo o administrativo:** modificación en requisitos, tasas o plazos
   para Cambio de Calidad a partir de enero 2026.
2. **Saturación de demanda:** los migrantes que querían regularizarse ya lo hicieron
   durante 2024-2025 y la demanda está en su nivel "estructural" más bajo.
3. **Efecto del Decreto Legislativo 1582 / nueva Ley Migratoria:** si hubo cambios
   regulatorios que alteraron los procedimientos vigentes.
4. **Represamiento y normalización:** hubo un pico artificial en 2025 por trámites
   acumulados de años anteriores, y 2026 refleja la demanda basal.

### Cómo se resolvería / qué información falta

- Consultar el portal oficial de Migraciones para identificar cambios normativos
  vigentes a partir de enero 2026.
- Revisar las notas de prensa de la Superintendencia Nacional de Migraciones
  (dic-2025 / ene-2026).
- Consultar con expertos en migración o abogados especializados si hay un cambio
  de régimen legal que explique la caída.
- Si en 2026-Q4 el nivel sigue estable, confirmar que el quiebre es permanente
  y el modelo `post_2026` es el correcto.
