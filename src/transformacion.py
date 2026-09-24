"""
src/transformacion.py
=====================
Funciones de transformación y construcción del panel mensual unificado.

Reglas de negocio aplicadas aquí:
1. Exclusión de duplicados en Carné de Extranjería:
   Los registros con TIPO_TRAMITE == "CAMBIO DE CALIDAD MIGRATORIA" se
   solapan con el dataset independiente "Cambio de Calidad Migratoria".
   Se excluyen para evitar doble conteo.

2. Columna 'regimen' (pre_2026 / post_2026):
   Aplicada solo a 'cambio_calidad' y 'carnet_extranjeria', que muestran
   un quiebre estructural de nivel confirmado entre diciembre 2025 y
   enero 2026 (caída de ≈50% no estacional).
"""

import pandas as pd

# Orden canónico de meses en español (tal como vienen en los CSV)
ORDEN_MESES = {
    "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4,
    "MAYO": 5, "JUNIO": 6, "JULIO": 7, "AGOSTO": 8,
    "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12,
}

# Tipos de trámite que tienen quiebre estructural 2025→2026
TRAMITES_CON_REGIMEN = {"cambio_calidad", "carnet_extranjeria"}


def normalizar_mes(serie: pd.Series) -> pd.Series:
    """Convierte nombres de mes en español a entero (1-12).

    Parameters
    ----------
    serie : pd.Series
        Serie con valores como 'ENERO', 'FEBRERO', etc.

    Returns
    -------
    pd.Series de int
    """
    mapeado = serie.str.strip().str.upper().map(ORDEN_MESES)
    n_invalidos = mapeado.isna().sum()
    if n_invalidos > 0:
        valores = serie[mapeado.isna()].unique().tolist()
        raise ValueError(
            f"Valores de MES_TRAMITE no reconocidos ({n_invalidos} filas): {valores}"
        )
    return mapeado.astype(int)


def construir_ds(df: pd.DataFrame) -> pd.Series:
    """Construye la columna 'ds' (primer día del mes) a partir de
    ANIO_TRAMITE y MES_TRAMITE.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con columnas ANIO_TRAMITE y MES_TRAMITE.

    Returns
    -------
    pd.Series de datetime64[ns]
    """
    anio = df["ANIO_TRAMITE"].astype(int)
    mes = normalizar_mes(df["MES_TRAMITE"])
    return pd.to_datetime(
        {"year": anio, "month": mes, "day": 1}
    )


def aplicar_regla_carnet(df: pd.DataFrame) -> pd.DataFrame:
    """Excluye los registros de Carné de Extranjería donde
    TIPO_TRAMITE == 'CAMBIO DE CALIDAD MIGRATORIA'.

    Solo actúa sobre filas donde tipo_tramite == 'carnet_extranjeria'.
    Para el resto del DataFrame no hace nada.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame concatenado de todos los trámites.

    Returns
    -------
    pd.DataFrame filtrado.
    """
    mask_carnet = df["tipo_tramite"] == "carnet_extranjeria"
    mask_solapo = (
        df["TIPO_TRAMITE"].str.strip().str.upper()
        == "CAMBIO DE CALIDAD MIGRATORIA"
    )
    filas_excluidas = (mask_carnet & mask_solapo).sum()
    if filas_excluidas > 0:
        print(
            f"[Regla 1 — Carné solapado] Se excluyen {filas_excluidas:,} filas "
            f"de Carné de Extranjería con TIPO_TRAMITE='CAMBIO DE CALIDAD MIGRATORIA'."
        )
    return df[~(mask_carnet & mask_solapo)].copy()


def agregar_regimen(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega la columna 'regimen' a los trámites con quiebre estructural.

    Valores posibles:
    - 'pre_2026':  ANIO_TRAMITE <= 2025
    - 'post_2026': ANIO_TRAMITE >= 2026
    - NaN:         trámites sin quiebre (Prórroga y Solicitud de Visas)

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con columnas 'tipo_tramite' y 'ANIO_TRAMITE'.

    Returns
    -------
    pd.DataFrame con la columna 'regimen' agregada.
    """
    df = df.copy()
    df["regimen"] = pd.NA

    mask = df["tipo_tramite"].isin(TRAMITES_CON_REGIMEN)
    anio = df.loc[mask, "ANIO_TRAMITE"].astype(int)
    df.loc[mask, "regimen"] = anio.apply(
        lambda a: "pre_2026" if a <= 2025 else "post_2026"
    )
    return df


def construir_panel_mensual(df: pd.DataFrame) -> pd.DataFrame:
    """Construye el panel mensual unificado en formato largo.

    Pasos:
    1. Aplica la regla de exclusión de duplicados en Carné (Regla 1).
    2. Construye 'ds' (primer día del mes).
    3. Agrega la columna 'regimen' (Regla 2).
    4. Convierte CANTIDAD a numérico.
    5. Agrega por (ds, tipo_tramite, sede, regimen) sumando CANTIDAD → y.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame concatenado de todos los CSV raw, con la columna
        'tipo_tramite' ya añadida por cargar_csv_raw / cargar_todos_los_raw.

    Returns
    -------
    pd.DataFrame con columnas:
        ds           — datetime64[ns], primer día del mes
        y            — int, suma de CANTIDAD
        tipo_tramite — str, clave corta del trámite
        sede         — str, SEDE_ATENCION
        regimen      — str | NA, 'pre_2026' / 'post_2026' / NA
    """
    # 1. Regla de negocio: excluir solapamiento en Carné
    df = aplicar_regla_carnet(df)

    # 2. Fecha (primer día del mes)
    df = df.copy()
    df["ds"] = construir_ds(df)

    # 3. Régimen (quiebre estructural)
    df = agregar_regimen(df)

    # 4. CANTIDAD numérica
    df["CANTIDAD"] = pd.to_numeric(df["CANTIDAD"], errors="coerce").fillna(0).astype(int)

    # 5. Columna de sede
    df["sede"] = df["SEDE_ATENCION"].str.strip().str.upper()

    # 6. Agregación mensual
    panel = (
        df.groupby(["ds", "tipo_tramite", "sede", "regimen"], dropna=False)["CANTIDAD"]
        .sum()
        .reset_index()
        .rename(columns={"CANTIDAD": "y"})
    )

    # Orden canónico de columnas
    panel = panel[["ds", "y", "tipo_tramite", "sede", "regimen"]]
    panel = panel.sort_values(["tipo_tramite", "sede", "ds"]).reset_index(drop=True)

    return panel
