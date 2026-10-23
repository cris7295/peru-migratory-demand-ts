# Auditoría previa al modelado — 23 de octubre de 2026

## Actualización posterior: fuentes y rama

Se continúa en `cris7295/auditoria-pre-modelado`, por solicitud de cris7295.
La identidad Git configurada sigue siendo Cris, la misma de los commits anteriores;
esta revisión todavía no tiene commits nuevos.

El bloqueo HTTP 403 consignado más abajo corresponde a la consulta web inicial.
Posteriormente se accedió a las cuatro páginas oficiales desde navegador. Sus tablas
públicas de campos confirman: cambio de calidad, visas y prórroga cuentan trámites
presentados; carné cuenta documentos emitidos. Esto resuelve la definición básica
del evento registrado y no acredita duplicación entre presentación y emisión.
Se localizaron los cuatro diccionarios; aún no se descargaron sus XLSX ni nuevos CSV.
Las páginas muestran modificación 2026-09-16: no se infiere cobertura de septiembre.
Ver `docs/fuentes_datos.md` para enlaces y evidencia actualizada.

## Dictamen

El proyecto puede iniciar experimentos controlados de fase 4, pero todavía no
puede presentar pronósticos como validados ni resolver con estos archivos la
madurez del último mes o la equivalencia de eventos entre fuentes.
Se corrigieron errores verificables y se documentaron hipótesis sin inventar evidencia.

## Contraste de las dos revisiones de IA

| Propuesta o afirmación | Dictamen y acción |
|---|---|
| Piura tiene pico en diciembre de 2025 | Correcto: 1.096 frente a 964 en enero. Corrige también la primera revisión del asistente |
| Enero–agosto y septiembre–diciembre estaban desbalanceados | Corregido: resumen por sede/año con meses observados y gráficos separados |
| Agosto de 2025 es anormal | Es el máximo observado, 10.340; no se ha demostrado error o anomalía estadística que permita eliminarlo |
| Quitar agosto demuestra subreporte | Incorrecto: efecto aritmético del recorte, no identificación causal |
| Si agosto sube en la siguiente descarga queda comprobado el subreporte | Confirma revisión al alza, pero falta distinguir carga tardía, corrección y reclasificación |
| Si no cambia, la baja es real | Incorrecto: puede no haberse actualizado o continuar incompleto; no prueba madurez |
| Ya debería existir septiembre | No comprobado. Los accesos consultados devolvieron HTTP 403 |
| Último mes provisional | Útil como política conservadora; no prueba incompletitud ni se vuelve definitivo automáticamente en la siguiente descarga |
| Tres meses como máximo | Propuesta prudente, no límite universal. Priorizar h=1,2; evaluar h=3; h=6 solo exploratorio sin respaldo suficiente |
| Corte septiembre y tres meses permiten probar enero | No: cubren octubre–diciembre. Enero requiere otra emisión o cuatro meses desde septiembre |
| Conservar el componente excluido de carné | Implementado en tabla separada; no anexarlo y sumar ambas vistas |
| Elegir carné con o sin filtro según error | Son objetivos distintos. La definición administrativa precede a la comparación predictiva |
| Faltantes solo importan al ampliar sedes | También pueden afectar la interpretación de totales nacionales si representan falta de reporte; no imputar cero |
| Usar promedio si gana | Correcto bajo comparación justa, mismas fechas/objetivo/horizonte y sin elegir en el conjunto de prueba |
| Revisar Granger en diciembre | Hito propuesto, no garantía de potencia o causalidad |

## Correcciones implementadas

1. Carga estricta de los ocho archivos: no continuar con un conjunto parcial.
2. Validación de columnas, claves, años, meses y cantidades antes de cualquier filtro.
   No convertir errores a cero ni truncar fracciones.
3. Panel histórico: se conservan todas sus claves y cantidades. Solo cambia `regimen`
   en las 360 filas de carné, que pasa a ausente para evitar una segmentación injustificada.
4. `carnet_componentes.csv`: 720 filas con dos componentes disjuntos; reconciliación
   por sede/mes contra el total de carné original y contra su subconjunto histórico.
5. EDA reescrito: comparación por año y períodos equivalentes; conclusiones prudentes
   sobre Granger, ADF, quiebres, causalidad y revisiones; eliminación de textos concluyentes falsos.
6. Referencias predictivas reproducibles, por corte, para h=1,2,3; reportan MAE, WAPE,
   sesgo y número de observaciones. No se entrena Prophet ni se selecciona un ganador.
7. Versionado de originales mediante copias y SHA-256. Comparador de versiones por
   sede/mes/subtipo, con ausencias NA y sin inferencias causales automáticas.
8. Pruebas sintéticas para errores de datos, cobertura estacional desigual, ausencia
   de fuga de futuro en referencias, reconciliación y conservación de snapshots.
9. Documentación alineada; propuesta de horizontes separada de los acuerdos históricos.

## Evidencia local

- Ocho originales, 113.440 filas y 1.375 filas del panel.
- Suma contable de fuentes: 1.073.704; componente de carné apartado: 121.343;
  panel histórico: 952.361. No son personas únicas ni prueba de eventos duplicados.
- Carné total de su fuente: 266.078; subconjunto histórico: 144.735.
- Enero–junio carné filtrado: +3,83 % interanual; enero–julio: +0,15 %;
  enero–agosto: −8,04 %. Comparaciones con los mismos meses del año previo.
- Cambio de calidad diciembre–enero: −51,74 %; causa sin confirmar.
- Prórroga top-5: 90,40 % del volumen; no es el total nacional.
- Cobertura: cuatro sede-mes ausentes de prórroga (Ica); 81 en visas. No se imputaron.

Referencias nacionales a un mes, evaluación exploratoria retrospectiva:

| Serie | Referencia | Errores evaluados | WAPE |
|---|---|---:|---:|
| Prórroga | Mismo mes del año previo | 8 | 9,95 % |
| Cambio de calidad, 2026 | Promedio previo de tres meses | 4 | 3,42 % |
| Carné filtrado, hasta julio | Promedio previo de tres meses | 7 | 6,69 % |
| Carné filtrado, con agosto | Promedio previo de tres meses | 8 | 8,28 % |
| Visas | Promedio previo de tres meses | 8 | 18,26 % |

Los dos escenarios de carné tienen muestras de evaluación distintas: su comparación
no justifica descartar agosto para reducir el error. Las referencias nacionales de
prórroga no sustituyen la evaluación pendiente por sede. El WAPE de cambio a h=2
es 2,36 % con tres errores y a h=3 es 2,92 % con dos: ni el tamaño de muestra ni
las fechas coinciden con h=1; no demuestra mayor precisión a largo plazo.

## Verificación realizada

- 12 pruebas de `unittest` aprobadas.
- Todas las celdas de código de los tres notebooks ejecutadas en orden, en procesos
  de análisis con contexto separado por notebook; no se guardaron salidas dentro de los ipynb.
- Recarga y reconciliación de ambos CSV procesados verificadas.
- Comparación contra el panel de HEAD: todos los conteos y claves idénticos; solo
  las 360 etiquetas de régimen del carné cambian.
- Ocho hashes de originales coinciden con sus copias conservadas.
- Gráficos renderizados e inspeccionados visualmente.
- El workflow incorpora las pruebas, pero no se ha ejecutado GitHub Actions ni publicado una rama.

Entorno observado: Python 3.10.6, pandas 2.3.3, numpy 2.2.6, Prophet 1.4.0,
statsmodels 0.15.0, matplotlib 3.10.9. CI y README señalan Python 3.11: todavía
no se verificó esta revisión en ese intérprete. El notebook solicita explícitamente el retorno ADF compatible cuando la versión
de statsmodels permite hacerlo. No se ocultan warnings globalmente.
Las versiones observadas y hashes de entradas/código están en `auditoria/ejecucion.json`;
no constituyen un lockfile completo de dependencias.

## Artefactos y reproducción

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m src.auditoria
```

Ejecutar notebooks 01 → 02 → 03 para reconstruir panel, componentes y visualizar EDA.
La exportación numérica usa los raw y no depende de salidas guardadas de notebooks.

- `auditoria/resumen.json`: conteos de control.
- `auditoria/estacionalidad_por_anio.csv`: picos, valles y cobertura anual.
- `auditoria/carnet_periodos_equivalentes.csv`: comparación interanual acumulada.
- `auditoria/cobertura.csv`: meses observados/ausentes por sede y trámite.
- `auditoria/predicciones_referencias.csv`: predicciones, cortes y valores reales.
- `auditoria/metricas_referencias.csv`: errores por serie/modelo/horizonte.
- `auditoria/manifest_raw.json`: manifiesto de la copia conservada en esta revisión.
- `auditoria/ejecucion.json`: hashes de entradas/código y versiones de la auditoría numérica.
- `auditoria/figura_01.png`, `figura_02.png`: gráficos generados durante la verificación.

Snapshot local: `data/raw/snapshots/20261023T204804777149Z/` (ignorado por Git).
La fecha corresponde a conservación, no a descarga. Los originales activos no se renombraron.

## Trabajo pendiente, en orden

1. Obtener diccionarios y una nueva versión oficial, conservarla separada y comparar
   revisiones sin reemplazar automáticamente la base de trabajo. Consulta del 23/10:
   páginas de carné/cambio y recurso carné devolvieron HTTP 403. No se descargaron nuevos datos.
2. Definir evento objetivo, destinatario del pronóstico y costos de sobre/subestimación.
   Completar el PRD con el equipo. Evitar llamar demanda latente a un conteo de emisión.
3. Acordar horizonte inicial y política de madurez; los cambios propuestos no se
   presentan como aprobados por ambos integrantes ni como evidencia ya validada.
4. Implementar fase 4 con referencias y Prophet sobre idénticos cortes/objetivos,
   poca complejidad, métricas por horizonte y selección separada de la prueba final.
5. Exportar para Power BI con corte, fecha de emisión, estado de dato, modelo,
   horizonte, definición de objetivo y límites de interpretación.

## Fuentes consultadas

- [Ficha indexada de carné 2026](https://www.datosabiertos.gob.pe/dataset/carnet-de-extranjeria/resource/de91e17d-0f27-4cae-9fc0-cc6bddd5d67d):
  describe carnés emitidos; acceso directo bloqueado al consultar.
- [Prophet, datos mensuales](https://facebook.github.io/prophet/docs/non-daily_data.html).
- [Prophet, validación temporal](https://facebook.github.io/prophet/docs/diagnostics.html).

La calidad se acredita con evidencia, reproducibilidad y revisión. Ninguna revisión
por IA sustituye la definición del dato ni convierte una hipótesis en un hecho.
