# Decisiones de modelado — revisión técnica previa a fase 4

Revisión: 2026-10-23. Sustituye las afirmaciones no sustentadas de la versión 1.0
(2026-09-24), conservada en Git. Las correcciones de evidencia se implementan en
esta rama; las propuestas de horizonte y selección aún no son resultados validados
ni se presentan como acuerdo nuevo de ambos integrantes del equipo.

## Objetivo y alcance

Predecir conteos mensuales por fuente, distinguiendo sus eventos. Verificación directa
posterior en navegador (2026-10-23): cambio de calidad, visas y prórroga miden trámites
presentados; carné mide documentos emitidos. La tabla pública de campos de cada
página confirma estas definiciones; los XLSX de diccionario quedan localizados.
No interpretar la suma como personas únicas, flujo migratorio o demanda insatisfecha.
La elección operativa entre carné total y un subconjunto sigue pendiente.

El panel histórico conserva cuatro categorías. `carnet_extranjeria` excluye el subtipo
CAMBIO DE CALIDAD MIGRATORIA y debe rotularse así, no como carné total o deduplicado.
`carnet_componentes.csv` conserva ese subtipo y los demás en dos componentes disjuntos.
Su suma recupera todo el carné de la fuente. No sumar esta tabla al panel histórico.
La coincidencia del nombre del procedimiento no prueba duplicación de eventos entre fuentes.
Comparar errores de carné total y filtrado no decide cuál es el objetivo correcto:
son variables distintas, que deben definirse por el uso operativo.

## Evidencia corregida

- Prórroga: enero elevado en las cinco sedes principales. En 2025 es el máximo
  en cuatro; en Piura diciembre registra 1.096 frente a 964 de enero. No hay valle
  común en septiembre. Se comparan años separados, sin sumar meses con distinta cobertura.
- Cambio de calidad: caída observada de 12.168 a 5.872 entre diciembre de 2025 y
  enero de 2026 (−51,74 %). Causa y permanencia sin confirmar; se retira la atribución normativa.
- Carné filtrado: enero–julio de 2026 cambia +0,15 % respecto de enero–julio de 2025;
  enero–agosto cambia −8,04 %. Agosto de 2025 fue alto (10.340) y agosto de 2026
  bajo (5.454). Ninguno queda declarado error, outlier eliminable o mes incompleto.
- Visas: Lima representa 94,43 % del volumen del panel, no 93,5 %.
- Datos: 20 meses nacionales. Volumen alto no aumenta el número de observaciones
  temporales. Modelar por sede no reduce necesariamente los meses: las cinco sedes
  de prórroga tienen 20 cada una; reduce el volumen por serie.

## Diseño de experimentos

| Serie | Preparación inicial | Candidatos y límites |
|---|---|---|
| Prórroga, cinco sedes | 20 meses por sede | Referencia anual, último valor, promedio reciente y Prophet con estacionalidad anual parsimoniosa; no asumir superioridad |
| Cambio de calidad, nacional | Escenario principal desde enero de 2026 | Promedio reciente, último valor y Prophet sin estacionalidad anual; ocho meses limitan evaluación y extrapolación |
| Carné filtrado, nacional | Historia continua; escenarios con y sin agosto | Comparación de sensibilidad, no selección de observaciones para mejorar el error; evitar separar por régimen |
| Carné total/componentes | Vista alternativa conservada | Definir primero el objetivo administrativo; luego evaluar cada objetivo por separado |
| Visas, nacional | 20 meses | Referencias simples y Prophet con/sin componente anual regularizado; ADF no decide estacionalidad |

El top-5 de prórroga representa 90,40 % del volumen y no constituye el total nacional.
Si se necesita un total, modelar el resto o entrenar/evaluar una serie nacional explícita.
Definir las sedes por alcance operativo antes del backtest; no seleccionarlas usando el futuro.

## Horizonte y validación: propuesta para fase 4

La versión 1.0 proponía seis meses. Propuesta revisada: prioridad operativa a uno y
 dos meses, evaluar también tres; seis solo como escenario exploratorio mientras
no exista evidencia suficiente. No existe una regla universal que haga tres meses
confiables y seis imposibles. El nivel de respaldo depende de cada serie y horizonte.

- Frecuencia mensual `MS`, sin componentes diarios o semanales.
- Cortes cronológicos explícitos y ventanas de entrenamiento expansivas; no partición aleatoria.
- Comparar modelos sobre exactamente el mismo objetivo, cortes y meses futuros.
- Reportar MAE, WAPE, sesgo y número de errores por horizonte; MAPE como complemento
  cuando sus denominadores lo permitan. Intervalos: reportar cobertura observada y límites.
- La selección ocurre en validación; reservar prueba temporal final cuando la historia
  lo permita. Si se explora repetidamente el último tramo, ya no es una prueba independiente.
- Con cuatro meses iniciales de cambio de calidad solo existen cuatro errores a h=1,
  tres a h=2 y dos a h=3. Los errores de cortes solapados tampoco son réplicas independientes.
- La referencia de promedio de tres meses obtuvo WAPE 3,42 % en cuatro errores a h=1.
  No trasladar ese resultado a otros horizontes ni declararlo ganador frente a Prophet,
  que aún no se ha entrenado. Si una referencia simple gana consistentemente bajo
  el protocolo acordado, puede ser el modelo final.
- Ajustar con pocos parámetros; 19–20 meses no garantizan identificar bien la
  estacionalidad anual. Evitar búsqueda extensa de hiperparámetros sobre pocos errores.
- Las métricas actuales usan una sola instantánea revisada: no reconstruyen qué se
  conocía en cada corte. Conservar versiones para una futura evaluación en tiempo real.

## Fechas de corte y revisiones

La fecha de proceso de los archivos 2026 es 2026-09-02; llegan hasta agosto.
No se ha confirmado una versión posterior. No inferir disponibilidad de septiembre
por la fecha actual ni identificar automáticamente el último mes como completo.

Propuesta de control: último mes con madurez no verificada = provisional, como
etiqueta conservadora, no como demostración de subreporte. Observarlo en una descarga
posterior no garantiza cierre: verificar fecha de proceso, versión y política de revisión.
Una subida confirma revisión al alza; podría deberse a carga tardía, correcciones o
reclasificación. La ausencia de cambios no demuestra que la demanda haya bajado realmente.

Un corte común facilita comparar modelos, pero debe tener evidencia de madurez o
etiquetarse como provisional. La fecha de ejecución y el horizonte desde el corte se
registran por separado. Corte septiembre + tres meses = octubre–diciembre; enero
queda fuera y se incorpora en la siguiente emisión o en un horizonte de cuatro meses.

## Granger y ADF

Resultados exploratorios, no prueba de causalidad. Granger tiene una señal en lag 2
(p≈0,024), con muestra pequeña, quiebre de nivel y múltiples pruebas. No incorporar
regresor externo en la primera comparación. No rechazar ADF no prueba no estacionariedad.
Revisión propuesta cuando estén disponibles datos hasta diciembre de 2026, con
cobertura y revisiones comprobadas; ese hito no garantiza potencia ni significancia.
No se afirma que 24 o 30 observaciones basten por sí mismas.

## Fuentes técnicas

- [Prophet: datos mensuales](https://facebook.github.io/prophet/docs/non-daily_data.html).
- [Prophet: validación temporal](https://facebook.github.io/prophet/docs/diagnostics.html).
- Evidencia local: `notebooks/03_eda_avanzado.ipynb`, `reports/auditoria/`.
- Auditoría y limitaciones externas: `reports/auditoria_pre_modelado.md`.
