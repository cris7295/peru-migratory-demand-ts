# Seguimiento de hallazgos de fase 3 — revisión 2026-10-23

Estas notas corrigen las afirmaciones de la revisión 2026-09-24, conservada en Git.
No acreditan que se hayan abierto o actualizado issues en GitHub.

| Hallazgo o tarea | Estado | Criterio de resolución |
|---|---|---|
| Suma estacional con cobertura desigual | Corregido | Comparar por sede y año; mostrar meses observados |
| Enero máximo universal / valle septiembre | Corregido | Piura máximo diciembre de 2025; valles distintos por sede |
| Causa normativa del descenso de cambio de calidad | Sin confirmar | Fuente oficial que vincule el cambio de registro o procedimiento con la caída |
| Agosto de carné subreportado | Sin confirmar | Comparar versiones y política de revisión; una revisión no identifica sola su causa |
| Coincidencia entre carné y cambio como duplicados | Sin confirmar | Diccionarios y definición de evento; no basta cuadrar totales |
| Subconjunto de carné descartado del panel | Conservado aparte | Dos componentes disjuntos reconcilian contra toda la fuente por sede/mes |
| Carga parcial y conversión de errores a cero | Corregido | Validaciones estrictas y pruebas automáticas |
| Meses ausentes por sede | Detectados, sin imputar | Aclarar reporte/actividad antes de rellenar; puede afectar interpretación nacional |
| Granger y ADF | Exploratorio | Nueva evaluación al disponer de datos hasta diciembre de 2026; sin promesa de potencia |
| Horizon de fase 4 | Propuesta revisada | Priorizar h=1,2; evaluar h=3, registrar evidencia por serie y horizonte |
| Predictor final | Pendiente | Comparar Prophet y referencias bajo idénticos cortes/objetivos |
| Definición del objetivo y PRD | Pendiente | Definir evento, usuario del pronóstico, error tolerable y uso operativo |

Evidencia reproducible: `python -m src.auditoria`.
Pruebas: `python -m unittest discover -s tests -v`.
