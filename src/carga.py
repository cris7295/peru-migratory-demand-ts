"""
src/carga.py
============
Funciones para leer los CSV raw del proyecto.

Convenciones de los archivos fuente:
- Delimitador: pipe (|)
- Saltos de línea: CRLF
- Encoding: UTF-8
- Columnas comunes: SEDE_ATENCION, ANIO_TRAMITE, MES_TRAMITE, CANTIDAD
"""

import os
from pathlib import Path
import pandas as pd


# Directorio raíz del repositorio (dos niveles arriba de src/)
ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT_DIR / "data" / "raw"

# Mapeo nombre_corto → patrón de nombre de archivo
TRAMITES = {
    "cambio_calidad": "CAMBIO DE CALIDAD MIGRATORIA",
    "carnet_extranjeria": "CARNET DE EXTRANJERIA",
    "prorroga_residencia": "PRORROGA DE RESIDENCIA",
    "solicitud_visas": "SOLICITUD DE CALIDAD MIGRATORIA (VISAS)",
}


def cargar_csv_raw(tipo_tramite: str, anio: int, raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Carga un CSV raw para un tipo de trámite y año dados.

    Parameters
    ----------
    tipo_tramite : str
        Clave corta del trámite. Valores válidos: 'cambio_calidad',
        'carnet_extranjeria', 'prorroga_residencia', 'solicitud_visas'.
    anio : int
        Año del archivo (2025 ó 2026).
    raw_dir : Path, optional
        Carpeta donde buscar los CSV. Por defecto: data/raw/.

    Returns
    -------
    pd.DataFrame
        DataFrame con los datos del CSV, más una columna 'tipo_tramite'
        con el nombre corto del trámite.

    Raises
    ------
    ValueError
        Si `tipo_tramite` no está en el mapeo conocido.
    FileNotFoundError
        Si el archivo no se encuentra en `raw_dir`.
    """
    if tipo_tramite not in TRAMITES:
        raise ValueError(
            f"tipo_tramite '{tipo_tramite}' no reconocido. "
            f"Opciones: {list(TRAMITES)}"
        )

    patron = TRAMITES[tipo_tramite]
    nombre_archivo = f"{patron} {anio}.csv"
    ruta = raw_dir / nombre_archivo

    if not ruta.exists():
        raise FileNotFoundError(
            f"Archivo no encontrado: {ruta}\n"
            f"Descárgalo desde docs/fuentes_datos.md y colócalo en data/raw/."
        )

    df = pd.read_csv(ruta, sep="|", encoding="utf-8", dtype=str)
    df["tipo_tramite"] = tipo_tramite
    return df


def cargar_todos_los_raw(anios: list[int] = None, raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Carga y concatena todos los CSV raw para los años indicados.

    Parameters
    ----------
    anios : list[int], optional
        Lista de años a cargar. Por defecto: [2025, 2026].
    raw_dir : Path, optional
        Carpeta donde buscar los CSV. Por defecto: data/raw/.

    Returns
    -------
    pd.DataFrame
        DataFrame concatenado con todos los trámites y años. Incluye la
        columna 'tipo_tramite' con la clave corta del trámite.
    """
    if anios is None:
        anios = [2025, 2026]

    partes = []
    for tipo in TRAMITES:
        for anio in anios:
            try:
                df = cargar_csv_raw(tipo, anio, raw_dir=raw_dir)
                partes.append(df)
            except FileNotFoundError as e:
                print(f"[ADVERTENCIA] {e}")

    if not partes:
        raise RuntimeError("No se pudo cargar ningún archivo CSV raw.")

    return pd.concat(partes, ignore_index=True)
