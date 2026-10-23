# Fuentes de Datos Oficiales

Este proyecto usa 4 datasets públicos de la Superintendencia Nacional de Migraciones,
publicados en la Plataforma Nacional de Datos Abiertos del Perú.

| Dataset | Rol en el proyecto | Enlace |
|---|---|---|
| Cambio de Calidad Migratoria | Dataset base / variable objetivo principal | https://www.datosabiertos.gob.pe/dataset/cambio-de-calidad-migratoria |
| Solicitud de Calidad Migratoria (Visas) | Complementario | https://www.datosabiertos.gob.pe/dataset/solicitud-de-calidad-migratoria-visas |
| Carné de Extranjería | Complementario | https://www.datosabiertos.gob.pe/dataset/carnet-de-extranjeria |
| Prórroga de Residencia | Complementario; modelado pendiente | https://www.datosabiertos.gob.pe/dataset/prorroga-de-residencia |

## ¿Por qué estos enlaces están aquí y no los archivos CSV directamente en el repositorio?

Guardamos los **enlaces**, no los archivos pesados, por tres razones simples:

1. **El repositorio se mantiene liviano.** Cada archivo pesa 1-2 MB y crecerá cada mes; si los
   vamos acumulando todos dentro de Git, el repositorio se vuelve pesado y lento con el tiempo.
2. **Cualquier persona puede obtener los datos más recientes** simplemente entrando al enlace y
   descargando el archivo actualizado, sin depender de una copia guardada que puede quedar vieja.
3. **Transparencia y trazabilidad.** Si alguien (nuestro compañero, un auditor, nosotros mismos en
   6 meses) quiere confirmar de dónde salió un número, el enlace lo lleva directo a la fuente oficial.

## Cómo se guardan los datos que sí usamos

- Los archivos CSV descargados se colocan en `data/raw/` (esa carpeta está excluida de Git,
  ver `.gitignore`) — cada quien los descarga localmente desde los enlaces de arriba.
- Los datos ya procesados y combinados (livianos, agregados por mes) sí se guardan en
  `data/processed/`, porque esos son pequeños y es útil tener el historial de cómo evolucionan.

## Nota sobre actualizaciones del portal

Revisión 2026-10-23: la consulta web automatizada devolvió HTTP 403, pero después
se accedió correctamente a las cuatro páginas mediante navegador. Se verificaron
la descripción y la tabla pública de campos (Additional Info), sin descargar todavía
los XLSX de diccionario ni nuevas copias de los CSV.

| Fuente | Significado oficial de CANTIDAD | Unidad que modelar |
|---|---|---|
| Cambio de Calidad Migratoria | Trámites de cambio de calidad presentados | Presentación de trámites |
| Solicitud de Calidad Migratoria (Visas) | Trámites de solicitud de calidad presentados | Presentación de solicitudes |
| Carné de Extranjería | Carnés de extranjería emitidos | Emisión de documentos |
| Prórroga de Residencia | Trámites de prórroga presentados | Presentación de trámites |

Las fuentes son las cuatro páginas enlazadas en la tabla inicial, confirmadas por
cris7295. Todas mostraban fecha de modificación 2026-09-16 y frecuencia mensual
al consultarlas. Esta fecha de página no demuestra cobertura de septiembre ni que
los CSV hayan cambiado respecto de la copia local.

En carné, TIPO_TRAMITE describe el procedimiento mediante el cual se emite el documento.
En las cuatro fuentes, FECHA_PROCESO describe el procesamiento de la información publicada.
Por tanto, presentación de cambio de calidad y emisión de un carné son etapas distintas:
no se justifica eliminar automáticamente una por considerarla duplicada de la otra.
Tampoco se justifica sumar ambas como personas únicas o como una sola medida homogénea
de demanda. El filtro histórico se conserva como subconjunto explícito hasta definir
el alcance operativo; todos los componentes permanecen disponibles.

Diccionarios oficiales localizados:

- [Cambio de calidad](https://www.datosabiertos.gob.pe/dataset/cambio-de-calidad-migratoria/resource/a998ac28-2d97-40f4-9103-8613b674d369).
- [Visas](https://www.datosabiertos.gob.pe/dataset/solicitud-de-calidad-migratoria-visas/resource/d7900ff3-28ef-4791-ae4c-c2b5aad5c7f5).
- [Carné](https://www.datosabiertos.gob.pe/dataset/carnet-de-extranjeria/resource/649495bf-34a5-48c4-a503-439c97c7409f).
- [Prórroga](https://www.datosabiertos.gob.pe/dataset/prorroga-de-residencia/resource/57d8ecdf-c78c-45aa-99c3-9274081fa479).

## Conservar y comparar versiones

Antes de reemplazar originales, ejecutar `python -m src.versiones --snapshot`.
Conserva los ocho archivos en `data/raw/snapshots/`, ignorado por Git, sin renombrar
los archivos activos. El manifiesto registra SHA-256, tamaño y fecha de proceso.
La fecha de conservación no se presenta como fecha de descarga.

Descargar la nueva versión en una carpeta separada y comprobar esquema, fechas de
proceso y cobertura. Para comparar dos carpetas completas de ocho originales:

```powershell
python -m src.versiones --anterior data/raw/snapshots/IDENTIFICADOR --nueva RUTA_NUEVA --salida reports/auditoria/revisiones.csv
```

El resultado preserva ausencias como NA y muestra revisiones por sede/mes/subtipo.
Una revisión al alza no identifica su causa; sin cambios tampoco se demuestra cierre.
No declarar completo un mes por haber aparecido en dos descargas iguales.

En 2025-2026 el portal reorganizó parte de sus datasets ("Datatón 2025"), lo que en su momento
generó enlaces rotos. Los enlaces de esta tabla fueron verificados manualmente contra el listado
oficial vigente de la entidad. Si alguno dejara de funcionar en el futuro, buscar el nombre exacto
del dataset (columna izquierda) directamente en https://www.datosabiertos.gob.pe/
