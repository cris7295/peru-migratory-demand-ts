"""Validaciones que impiden convertir errores de origen en demanda cero."""

import numpy as np
import pandas as pd

ORDEN_MESES = {
    "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4,
    "MAYO": 5, "JUNIO": 6, "JULIO": 7, "AGOSTO": 8,
    "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12,
}
TIPOS = {"cambio_calidad", "carnet_extranjeria", "prorroga_residencia", "solicitud_visas"}


def normalizar_mes(serie: pd.Series) -> pd.Series:
    mapeado = serie.astype("string").str.strip().str.upper().map(ORDEN_MESES)
    if mapeado.isna().any():
        raise ValueError("MES_TRAMITE contiene meses ausentes o no reconocidos.")
    return mapeado.astype(int)


def validar_raw(df: pd.DataFrame, anio_esperado: int | None = None) -> None:
    """Rechaza esquema incompleto, claves vacías y conteos inválidos, sin imputar."""
    requeridas = {"SEDE_ATENCION", "ANIO_TRAMITE", "MES_TRAMITE", "CANTIDAD", "tipo_tramite"}
    faltantes = requeridas - set(df.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {sorted(faltantes)}")
    if df.empty:
        raise ValueError("El archivo o conjunto de datos está vacío.")
    for columna in requeridas:
        valores = df[columna].astype("string").str.strip()
        if (valores.isna() | valores.eq("")).any():
            raise ValueError(f"{columna} contiene valores ausentes o vacíos.")
    if not df["tipo_tramite"].isin(TIPOS).all():
        raise ValueError("tipo_tramite contiene categorías no reconocidas.")
    cantidades = pd.to_numeric(df["CANTIDAD"], errors="coerce")
    invalidas = (~np.isfinite(cantidades)) | (cantidades < 0) | (cantidades % 1 != 0)
    if invalidas.any():
        raise ValueError(f"CANTIDAD: {int(invalidas.sum())} valores no finitos, negativos o no enteros.")
    anios = pd.to_numeric(df["ANIO_TRAMITE"], errors="coerce")
    if ((~np.isfinite(anios)) | (anios % 1 != 0) | ~anios.between(1900, 2200)).any():
        raise ValueError("ANIO_TRAMITE contiene años inválidos.")
    if anio_esperado is not None and not anios.eq(anio_esperado).all():
        raise ValueError(f"ANIO_TRAMITE no corresponde al año solicitado: {anio_esperado}.")
    normalizar_mes(df["MES_TRAMITE"])
    carnet = df["tipo_tramite"].eq("carnet_extranjeria")
    if carnet.any():
        if "TIPO_TRAMITE" not in df:
            raise ValueError("Falta TIPO_TRAMITE para clasificar los registros de carné.")
        subtipos = df.loc[carnet, "TIPO_TRAMITE"].astype("string").str.strip()
        if (subtipos.isna() | subtipos.eq("")).any():
            raise ValueError("TIPO_TRAMITE contiene subtipos de carné ausentes o vacíos.")
