"""Instantáneas de archivos originales y comparación descriptiva de revisiones."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from datetime import datetime, timezone

import pandas as pd

from src.carga import RAW_DIR, TRAMITES, cargar_todos_los_raw
from src.calidad import validar_raw
from src.transformacion import construir_ds


def guardar_snapshot(raw_dir: Path = RAW_DIR, destino: Path | None = None) -> Path:
    """Copia los ocho originales sin renombrarlos ni sobrescribir snapshots.

    Fecha de conservación no significa fecha de descarga. Las fechas de proceso
    se registran por separado. El manifiesto contiene hashes de los bytes copiados.
    """
    cargar_todos_los_raw(raw_dir=raw_dir)  # Valida el conjunto antes de crear la copia.
    instante = datetime.now(timezone.utc)
    destino = destino or raw_dir / "snapshots" / instante.strftime("%Y%m%dT%H%M%S%fZ")
    if destino.exists():
        raise FileExistsError(f"La instantánea ya existe: {destino}")
    destino.mkdir(parents=True)
    archivos = []
    for tipo, nombre in TRAMITES.items():
        for anio in (2025, 2026):
            origen = raw_dir / f"{nombre} {anio}.csv"
            copia = destino / origen.name
            shutil.copy2(origen, copia)
            contenido = copia.read_bytes()
            df = pd.read_csv(copia, sep="|", dtype=str)
            archivos.append({"archivo": origen.name, "tipo_tramite": tipo, "anio": anio,
                             "sha256": hashlib.sha256(contenido).hexdigest(), "bytes": len(contenido),
                             "fecha_proceso": sorted(df.FECHA_PROCESO.dropna().unique().tolist())
                             if "FECHA_PROCESO" in df else []})
    manifiesto = {"conservado_en_utc": instante.isoformat(), "fecha_descarga": "desconocida",
                  "archivos": archivos}
    (destino / "manifest.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2), encoding="utf-8")
    return destino


def comparar_versiones(anterior: pd.DataFrame, nueva: pd.DataFrame) -> pd.DataFrame:
    """Comparación por mes/tipo/sede; ausencias quedan NA, nunca cero.

    Una revisión no identifica su causa; sin revisión tampoco se demuestra cierre.
    Se conserva TIPO_TRAMITE en carné para detectar reclasificaciones de subtipos.
    """
    def agregar(df):
        validar_raw(df)
        df = df.copy()
        df["ds"] = construir_ds(df)
        df["sede"] = df.SEDE_ATENCION.str.strip().str.upper()
        df["subtipo"] = "no_aplica"
        mask = df.tipo_tramite.eq("carnet_extranjeria")
        if mask.any():
            df.loc[mask, "subtipo"] = df.loc[mask, "TIPO_TRAMITE"].str.strip().str.upper()
        df["y"] = pd.to_numeric(df.CANTIDAD, errors="raise")
        return df.groupby(["ds", "tipo_tramite", "sede", "subtipo"], as_index=False).y.sum()
    claves = ["ds", "tipo_tramite", "sede", "subtipo"]
    result = agregar(anterior).merge(agregar(nueva), on=claves, how="outer",
                                    suffixes=("_anterior", "_nueva"), indicator="presencia")
    result["delta"] = result.y_nueva - result.y_anterior
    result["delta_pct"] = 100 * result.delta / result.y_anterior.where(result.y_anterior.ne(0))
    return result.sort_values(claves).reset_index(drop=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", action="store_true")
    parser.add_argument("--anterior", type=Path)
    parser.add_argument("--nueva", type=Path)
    parser.add_argument("--salida", type=Path)
    args = parser.parse_args()
    if args.snapshot:
        if args.anterior or args.nueva or args.salida:
            parser.error("--snapshot no se combina con comparación.")
        print(guardar_snapshot())
    elif args.anterior and args.nueva and args.salida:
        comparacion = comparar_versiones(cargar_todos_los_raw(raw_dir=args.anterior),
                                         cargar_todos_los_raw(raw_dir=args.nueva))
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        comparacion.to_csv(args.salida, index=False, date_format="%Y-%m-%d")
    else:
        parser.error("Usa --snapshot o --anterior CARPETA --nueva CARPETA --salida CSV.")
