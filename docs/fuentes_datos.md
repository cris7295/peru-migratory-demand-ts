# Fuentes de Datos Oficiales

Este proyecto usa 4 datasets públicos de la Superintendencia Nacional de Migraciones,
publicados en la Plataforma Nacional de Datos Abiertos del Perú.

| Dataset | Rol en el proyecto | Enlace |
|---|---|---|
| Cambio de Calidad Migratoria | Dataset base / variable objetivo principal | https://www.datosabiertos.gob.pe/dataset/cambio-de-calidad-migratoria |
| Solicitud de Calidad Migratoria (Visas) | Complementario | https://www.datosabiertos.gob.pe/dataset/solicitud-de-calidad-migratoria-visas |
| Carné de Extranjería | Complementario | https://www.datosabiertos.gob.pe/dataset/carnet-de-extranjeria |
| Prórroga de Residencia | Complementario (modelo Prophet listo) | https://www.datosabiertos.gob.pe/dataset/prorroga-de-residencia |

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

En 2025-2026 el portal reorganizó parte de sus datasets ("Datatón 2025"), lo que en su momento
generó enlaces rotos. Los enlaces de esta tabla fueron verificados manualmente contra el listado
oficial vigente de la entidad. Si alguno dejara de funcionar en el futuro, buscar el nombre exacto
del dataset (columna izquierda) directamente en https://www.datosabiertos.gob.pe/
