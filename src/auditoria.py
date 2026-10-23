"""Cálculos reproducibles de la auditoría previa al modelado.

Ejecutar desde la raíz: python -m src.auditoria
No entrena Prophet ni selecciona un modelo definitivo.
"""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import sys
import numpy as np
import pandas as pd

from src.carga import cargar_todos_los_raw, ROOT_DIR, RAW_DIR, TRAMITES
from src.transformacion import construir_panel_mensual, construir_componentes_carnet


def resumen_estacional(panel: pd.DataFrame) -> pd.DataFrame:
    """Picos por sede y año; muestra cuántos meses sustentan cada comparación."""
    pr = panel.loc[panel.tipo_tramite.eq("prorroga_residencia")].copy()
    pr["anio"] = pr.ds.dt.year
    rows = []
    for (sede, anio), g in pr.groupby(["sede", "anio"]):
        s = g.groupby("ds").y.sum().sort_index()
        ene = s.loc[s.index.month == 1]
        rows.append({
            "sede": sede, "anio": anio, "meses_observados": len(s),
            "meses_pico": ",".join(str(d.month) for d in s.index[s.eq(s.max())]),
            "meses_valle": ",".join(str(d.month) for d in s.index[s.eq(s.min())]),
            "enero": float(ene.iloc[0]) if len(ene) else np.nan,
            "promedio_observado": s.mean(),
            "ratio_enero_promedio": float(ene.iloc[0] / s.mean()) if len(ene) and s.mean() else np.nan,
        })
    return pd.DataFrame(rows)


def comparar_periodos(serie: pd.Series, anio_base=2025, anio_actual=2026) -> pd.DataFrame:
    """Compara enero..mes con idéntica cobertura; omite períodos incompletos."""
    rows = []
    for mes in range(1, 13):
        fechas_a = pd.date_range(f"{anio_base}-01-01", periods=mes, freq="MS")
        fechas_b = pd.date_range(f"{anio_actual}-01-01", periods=mes, freq="MS")
        a, b = serie.reindex(fechas_a), serie.reindex(fechas_b)
        if a.isna().any() or b.isna().any():
            continue
        rows.append({"mes_final": mes, "total_base": a.sum(), "total_actual": b.sum(),
                     "variacion_pct": 100 * (b.sum() / a.sum() - 1) if a.sum() else np.nan})
    return pd.DataFrame(rows)


def evaluar_referencias(serie: pd.Series, inicial: int, horizontes=(1, 2, 3)) -> pd.DataFrame:
    """Origen móvil expansivo. Cada h usa solo datos hasta su propio corte.

    El promedio de tres meses queda fijo durante cada pronóstico multihorizonte.
    Las métricas de modelos solo son comparables si comparten fechas y horizontes.
    """
    serie = serie.sort_index()
    if not isinstance(serie.index, pd.DatetimeIndex) or serie.index.has_duplicates:
        raise ValueError("Se requiere un DatetimeIndex único.")
    calendario = pd.date_range(serie.index.min(), serie.index.max(), freq="MS")
    if not serie.index.equals(calendario) or serie.isna().any():
        raise ValueError("La serie debe ser mensual continua, sin imputar meses ausentes.")
    if not np.isfinite(serie).all() or (serie < 0).any():
        raise ValueError("La serie contiene valores no finitos o negativos.")
    if inicial < 3 or inicial >= len(serie) or any(h < 1 or h > 12 for h in horizontes):
        raise ValueError("Entrenamiento inicial u horizontes incompatibles con la serie.")
    rows = []
    for n in range(inicial, len(serie)):
        train = serie.iloc[:n]
        for h in horizontes:
            idx = n + h - 1
            if idx >= len(serie):
                continue
            candidatos = {"ultimo_valor": train.iloc[-1], "promedio_3m": train.iloc[-3:].mean()}
            # Todos los cortes del escenario deben poder usar la referencia anual.
            if inicial >= 12:
                candidatos["estacional_12m"] = train.iloc[idx - 12]
            for modelo, pred in candidatos.items():
                rows.append({"corte": train.index[-1], "ds": serie.index[idx], "h": h,
                             "modelo": modelo, "y": serie.iloc[idx], "yhat": pred})
    return pd.DataFrame(rows)


def metricas_referencias(pred: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (serie, modelo, h), g in pred.groupby(["serie", "modelo", "h"]):
        e = g.yhat - g.y
        rows.append({"serie": serie, "modelo": modelo, "h": h, "n": len(g),
                     "mae": e.abs().mean(), "wape_pct": 100 * e.abs().sum() / g.y.sum()
                     if g.y.sum() else np.nan, "sesgo": e.mean()})
    return pd.DataFrame(rows)


def generar_auditoria(destino: Path | None = None) -> dict:
    destino = destino or ROOT_DIR / "reports" / "auditoria"
    destino.mkdir(parents=True, exist_ok=True)
    raw = cargar_todos_los_raw()
    entradas = []
    for tipo, nombre in TRAMITES.items():
        for anio in (2025, 2026):
            ruta = RAW_DIR / f"{nombre} {anio}.csv"
            entradas.append({"archivo": ruta.name,
                             "sha256": hashlib.sha256(ruta.read_bytes()).hexdigest()})
    entorno = {"python": sys.version, "entradas": entradas,
               "paquetes": {p: importlib.metadata.version(p)
                            for p in ["pandas", "numpy", "statsmodels", "prophet", "matplotlib"]},
               "codigo": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (ROOT_DIR / "src").glob("*.py")}}
    (destino / "ejecucion.json").write_text(json.dumps(entorno, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    panel = construir_panel_mensual(raw)
    componentes = construir_componentes_carnet(raw)
    nacional = panel.pivot_table(index="ds", columns="tipo_tramite", values="y", aggfunc="sum")
    resumen_estacional(panel).to_csv(destino / "estacionalidad_por_anio.csv", index=False)
    comparar_periodos(nacional.carnet_extranjeria).to_csv(destino / "carnet_periodos_equivalentes.csv", index=False)
    nacional.to_csv(destino / "series_nacionales.csv")
    cobertura = panel.groupby(["tipo_tramite", "sede"]).ds.nunique().rename("meses_observados").reset_index()
    cobertura["meses_en_ventana"] = cobertura.tipo_tramite.map(panel.groupby("tipo_tramite").ds.nunique())
    cobertura["meses_ausentes"] = cobertura.meses_en_ventana - cobertura.meses_observados
    cobertura.to_csv(destino / "cobertura.csv", index=False)
    evaluaciones = []
    for tipo in nacional:
        s = nacional[tipo]
        if tipo == "cambio_calidad":
            s = s.loc["2026-01-01":]
            escenarios = [(tipo, s, 4)]
        elif tipo == "carnet_extranjeria":
            escenarios = [(tipo + "_hasta_julio", s.loc[:"2026-07-01"], 12),
                          (tipo + "_con_agosto", s.loc[:"2026-08-01"], 12)]
        else:
            escenarios = [(tipo, s, 12)]
        for nombre, datos, inicial in escenarios:
            evaluaciones.append(evaluar_referencias(datos, inicial).assign(serie=nombre))
    preds = pd.concat(evaluaciones, ignore_index=True)
    preds.to_csv(destino / "predicciones_referencias.csv", index=False, date_format="%Y-%m-%d")
    metricas_referencias(preds).to_csv(destino / "metricas_referencias.csv", index=False)
    resumen = {
        "filas_raw": len(raw), "filas_panel": len(panel),
        "cantidad_raw": int(pd.to_numeric(raw.CANTIDAD).sum()),
        "cantidad_panel": int(panel.y.sum()),
        "cantidad_componente_cambio_carnet": int(componentes.loc[
            componentes.componente.eq("asociado_cambio_calidad"), "y"].sum()),
        "nota": "Sumas contables entre fuentes: no equivalen a personas únicas ni acreditan duplicación.",
        "primer_mes": str(panel.ds.min().date()), "ultimo_mes": str(panel.ds.max().date()),
        "evaluacion": "Exploratoria retrospectiva sobre una instantánea; no valida datos disponibles en tiempo real.",
    }
    (destino / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return resumen


if __name__ == "__main__":
    print(json.dumps(generar_auditoria(), ensure_ascii=False, indent=2))
