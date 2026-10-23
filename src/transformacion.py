"""Panel mensual y componentes del carné, sin presuponer eventos duplicados.

El filtro histórico define un subconjunto. Los componentes se conservan en una
vista separada, no aditiva con el panel. Régimen es una etiqueta temporal.
"""
import pandas as pd
from src.calidad import ORDEN_MESES, normalizar_mes, validar_raw

TRAMITES_CON_REGIMEN = {"cambio_calidad"}
SUBTIPO_CAMBIO = "CAMBIO DE CALIDAD MIGRATORIA"


def construir_ds(df: pd.DataFrame) -> pd.Series:
    return pd.to_datetime({
        "year": pd.to_numeric(df["ANIO_TRAMITE"]).astype(int),
        "month": normalizar_mes(df["MES_TRAMITE"]), "day": 1,
    })


def _mascara_componente_cambio(df: pd.DataFrame) -> pd.Series:
    if "TIPO_TRAMITE" not in df:
        return pd.Series(False, index=df.index)
    return (
        df["tipo_tramite"].eq("carnet_extranjeria")
        & df["TIPO_TRAMITE"].astype("string").str.strip().str.upper().eq(SUBTIPO_CAMBIO)
    ).fillna(False)


def aplicar_regla_carnet(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica el filtro histórico; no identifica duplicados entre datasets."""
    validar_raw(df)
    return df.loc[~_mascara_componente_cambio(df)].copy()


def agregar_regimen(df: pd.DataFrame) -> pd.DataFrame:
    """Etiqueta pre/post-2026 solo en cambio_calidad; no atribuye una causa."""
    df = df.copy()
    df["regimen"] = pd.Series(pd.NA, index=df.index, dtype="string")
    mask = df["tipo_tramite"].isin(TRAMITES_CON_REGIMEN)
    anio = pd.to_numeric(df.loc[mask, "ANIO_TRAMITE"])
    df.loc[mask, "regimen"] = anio.map(lambda a: "pre_2026" if a <= 2025 else "post_2026")
    return df


def construir_panel_mensual(df: pd.DataFrame) -> pd.DataFrame:
    """Preserva los conteos históricos y rechaza errores antes del filtro.

    No rellena meses ausentes. carnet_extranjeria excluye el subtipo CAMBIO DE
    CALIDAD MIGRATORIA: no representa todos los carnés emitidos.
    """
    df = aplicar_regla_carnet(df)
    df["ds"] = construir_ds(df)
    df = agregar_regimen(df)
    df["CANTIDAD"] = pd.to_numeric(df["CANTIDAD"], errors="raise").astype("int64")
    df["sede"] = df["SEDE_ATENCION"].str.strip().str.upper()
    panel = (
        df.groupby(["ds", "tipo_tramite", "sede", "regimen"], dropna=False)["CANTIDAD"]
        .sum().reset_index().rename(columns={"CANTIDAD": "y"})
    )
    return panel[["ds", "y", "tipo_tramite", "sede", "regimen"]].sort_values(
        ["tipo_tramite", "sede", "ds"]
    ).reset_index(drop=True)


def construir_componentes_carnet(df: pd.DataFrame) -> pd.DataFrame:
    """Dos componentes disjuntos cuya suma recupera el dataset original de carné.

    Vista alternativa: NO anexar al panel y sumar ambas tablas. No materializa
    componentes ausentes como cero, ni deduplica personas o procedimientos.
    """
    validar_raw(df)
    carnet = df.loc[df["tipo_tramite"].eq("carnet_extranjeria")].copy()
    if carnet.empty:
        return pd.DataFrame(columns=["ds", "sede", "componente", "y"])
    carnet["componente"] = "otros_tramites"
    carnet.loc[_mascara_componente_cambio(carnet), "componente"] = "asociado_cambio_calidad"
    carnet["ds"] = construir_ds(carnet)
    carnet["sede"] = carnet["SEDE_ATENCION"].str.strip().str.upper()
    carnet["y"] = pd.to_numeric(carnet["CANTIDAD"], errors="raise").astype("int64")
    return carnet.groupby(["ds", "sede", "componente"], as_index=False)["y"].sum()
