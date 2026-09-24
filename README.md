# Predicción de Demanda de Trámites Migratorios — Perú

Proyecto de análisis de datos y predicción (con [Prophet](https://facebook.github.io/prophet/))
sobre la demanda de trámites migratorios en el Perú, usando datos públicos oficiales de la
Superintendencia Nacional de Migraciones. El resultado final se presenta en un dashboard de
Power BI.

📄 El documento de referencia del proyecto (objetivos, fases, alcance) está en
[`docs/PRD.md`](docs/PRD.md).
📊 Las fuentes de datos oficiales usadas están detalladas en
[`docs/fuentes_datos.md`](docs/fuentes_datos.md).

## Cómo instalar y correr el proyecto

Estos pasos asumen que ya tienes instalado [Python 3.11](https://www.python.org/downloads/),
[Git](https://git-scm.com/downloads) y [VSCode](https://code.visualstudio.com/download).

1. **Clonar el repositorio**
   ```
   git clone https://github.com/cris7295/peru-migratory-demand-ts.git
   cd peru-migratory-demand-ts
   ```

2. **Crear un entorno virtual de Python** (para no mezclar las librerías de este proyecto con
   otras que tengas instaladas)
   ```
   python -m venv .venv
   ```
   Activarlo:
   - En Windows: `.venv\Scripts\activate`
   - En Mac/Linux: `source .venv/bin/activate`

3. **Instalar las librerías necesarias**
   ```
   pip install -r requirements.txt
   ```

4. **Abrir la carpeta en VSCode**
   ```
   code .
   ```
   Al abrirlo, VSCode debería ofrecerte instalar las extensiones recomendadas del proyecto
   automáticamente. Si no, revisa la lista completa en `docs/PRD.md`, sección "Stack Tecnológico".

5. **Descargar los datasets**
   Los archivos de datos no están incluidos en este repositorio (ver `data/raw/README.md` para
   el porqué). Descárgalos desde los enlaces oficiales en `docs/fuentes_datos.md` y colócalos
   en la carpeta `data/raw/`.

6. **Correr los notebooks**
   Abre la carpeta `notebooks/` en VSCode con la extensión de Jupyter instalada, y corre los
   notebooks en el orden numerado (`01_...`, `02_...`, etc.).

## Estructura del repositorio

```
├── data/
│   ├── raw/          → datasets originales descargados (no se suben a GitHub)
│   └── processed/     → datos ya limpios y unificados
├── notebooks/         → exploración de datos y prototipos de modelos
├── src/                → funciones de Python reutilizables
├── reports/            → hallazgos y resultados listos para compartir
├── docs/
│   ├── PRD.md          → documento de referencia del proyecto
│   └── fuentes_datos.md → enlaces oficiales de los datasets
└── requirements.txt    → librerías de Python necesarias
```

## Dashboard final (Power BI)

> 🚧 Esta sección se completa en la Fase 6 del proyecto (ver `docs/PRD.md`), una vez que el
> dashboard esté construido. Acá se agregarán capturas de pantalla del resultado final.

<!-- Ejemplo de cómo se agregará una captura más adelante:
![Vista general del dashboard](docs/img/dashboard_general.png)
-->

## Estado del proyecto

En desarrollo. Ver las fases detalladas en [`docs/PRD.md`](docs/PRD.md) para saber en qué
etapa está el proyecto actualmente.

## Equipo

Proyecto desarrollado por [@cris7295](https://github.com/cris7295) y colaborador(es).
