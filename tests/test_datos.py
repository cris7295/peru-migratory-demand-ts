"""Regresiones de calidad y evidencia; no requieren CSV privados para CI."""
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.carga import cargar_csv_raw, cargar_todos_los_raw, TRAMITES
from src.transformacion import construir_panel_mensual, construir_componentes_carnet
from src.auditoria import resumen_estacional, comparar_periodos, evaluar_referencias
from src.versiones import comparar_versiones, guardar_snapshot


def muestra():
    return pd.DataFrame([
        ["LIMA", "2025", "ENERO", "10", "cambio_calidad", None],
        ["LIMA", "2025", "ENERO", "7", "carnet_extranjeria", "CAMBIO DE CALIDAD MIGRATORIA"],
        ["LIMA", "2025", "ENERO", "4", "carnet_extranjeria", "RENOVACION"],
        ["LIMA", "2026", "ENERO", "3", "cambio_calidad", None],
    ], columns=["SEDE_ATENCION", "ANIO_TRAMITE", "MES_TRAMITE", "CANTIDAD", "tipo_tramite", "TIPO_TRAMITE"])


class CalidadTests(unittest.TestCase):
    def test_no_oculta_cantidades_invalidas_incluso_en_filas_excluidas(self):
        for valor in ["texto", None, "", "-1", "1.5", "inf", "NaN"]:
            with self.subTest(valor=valor):
                raw = muestra(); raw.loc[1, "CANTIDAD"] = valor
                with self.assertRaises(ValueError):
                    construir_panel_mensual(raw)

    def test_claves_invalidas_fallan(self):
        for col, valor in [("SEDE_ATENCION", "  "), ("MES_TRAMITE", "OTRO"),
                           ("ANIO_TRAMITE", "2025.5"), ("TIPO_TRAMITE", None)]:
            with self.subTest(col=col):
                raw = muestra(); raw.loc[1, col] = valor
                with self.assertRaises(ValueError):
                    construir_panel_mensual(raw)

    def test_componentes_reconcilian_sin_alterar_panel_historico(self):
        raw = muestra(); panel = construir_panel_mensual(raw); comp = construir_componentes_carnet(raw)
        self.assertEqual(panel.y.sum(), 17)
        self.assertEqual(comp.y.sum(), 11)
        self.assertEqual(comp.loc[comp.componente.eq("otros_tramites"), "y"].sum(), 4)
        self.assertEqual(comp.loc[comp.componente.eq("asociado_cambio_calidad"), "y"].sum(), 7)
        self.assertTrue(panel.loc[panel.tipo_tramite.eq("carnet_extranjeria"), "regimen"].isna().all())
        self.assertEqual(set(panel.loc[panel.tipo_tramite.eq("cambio_calidad"), "regimen"]), {"pre_2026", "post_2026"})

    def test_no_rellena_meses_ausentes(self):
        panel = construir_panel_mensual(muestra())
        self.assertEqual(panel.ds.nunique(), 2)
        self.assertFalse(panel.y.eq(0).any())

    def test_archivo_faltante_no_genera_carga_parcial(self):
        with tempfile.TemporaryDirectory() as carpeta:
            root = Path(carpeta)
            muestra().iloc[[0]].drop(columns="tipo_tramite").to_csv(
                root / f"{TRAMITES['cambio_calidad']} 2025.csv", sep="|", index=False)
            with self.assertRaises(FileNotFoundError):
                cargar_todos_los_raw([2025], root)

    def test_anio_archivo_y_lista_anios(self):
        with tempfile.TemporaryDirectory() as carpeta:
            root = Path(carpeta)
            muestra().iloc[[0]].drop(columns="tipo_tramite").to_csv(
                root / f"{TRAMITES['cambio_calidad']} 2026.csv", sep="|", index=False)
            with self.assertRaises(ValueError):
                cargar_csv_raw("cambio_calidad", 2026, root)
        for anios in [[], [2025, 2025]]:
            with self.assertRaises(ValueError):
                cargar_todos_los_raw(anios)


class EvidenciaTests(unittest.TestCase):
    def test_pico_anual_no_mezcla_coberturas(self):
        ds = pd.date_range("2025-01-01", periods=20, freq="MS")
        y = [9] + [5] * 10 + [11] + [10] + [5] * 7
        panel = pd.DataFrame({"ds": ds, "y": y, "sede": "PIURA", "tipo_tramite": "prorroga_residencia"})
        r = resumen_estacional(panel).set_index("anio")
        self.assertEqual(r.loc[2025, "meses_pico"], "12")
        self.assertEqual(r.loc[2026, "meses_pico"], "1")
        self.assertEqual(r.loc[2026, "meses_observados"], 8)

    def test_comparacion_interanual_ignora_meses_no_comparables(self):
        ds = pd.date_range("2025-01-01", periods=20, freq="MS")
        s = pd.Series([10] * 8 + [100] * 4 + [10] * 8, index=ds)
        r = comparar_periodos(s)
        self.assertTrue(r.variacion_pct.eq(0).all())
        self.assertEqual(r.mes_final.max(), 8)

    def test_referencias_no_consumen_futuro(self):
        s = pd.Series(np.arange(1, 21), index=pd.date_range("2025-01-01", periods=20, freq="MS"))
        original = evaluar_referencias(s, 12)
        s.iloc[12:] = 99999
        modificado = evaluar_referencias(s, 12)
        a = original[original.corte.eq("2025-12-01")]
        b = modificado[modificado.corte.eq("2025-12-01")]
        np.testing.assert_equal(a.yhat.to_numpy(), b.yhat.to_numpy())
        self.assertTrue(a.loc[a.modelo.eq("promedio_3m"), "yhat"].eq(11).all())
        self.assertEqual(a.loc[a.modelo.eq("estacional_12m"), "yhat"].tolist(), [1, 2, 3])

    def test_referencias_rechazan_huecos(self):
        s = pd.Series(range(6), index=pd.date_range("2025-01-01", periods=6, freq="MS"))
        with self.assertRaises(ValueError):
            evaluar_referencias(s.drop(s.index[2]), 3)

    def test_revisiones_no_imputan_ausencia(self):
        old = muestra(); new = old.copy(); new.loc[2, "CANTIDAD"] = "6"
        new = new.iloc[1:]
        r = comparar_versiones(old, new)
        self.assertEqual(r.loc[r.subtipo.eq("RENOVACION"), "delta"].iloc[0], 2)
        self.assertTrue(r.loc[r.presencia.eq("left_only"), "y_nueva"].isna().all())
        self.assertTrue(r.loc[r.presencia.eq("left_only"), "delta"].isna().all())

    def test_snapshot_preserva_bytes_y_rechaza_sobrescritura(self):
        with tempfile.TemporaryDirectory() as carpeta:
            root = Path(carpeta)
            for tipo, nombre in TRAMITES.items():
                for anio in [2025, 2026]:
                    r = muestra().iloc[[2]].copy()
                    r["tipo_tramite"] = tipo; r["ANIO_TRAMITE"] = str(anio)
                    r.to_csv(root / f"{nombre} {anio}.csv", sep="|", index=False)
            destino = root / "snapshot"
            guardar_snapshot(root, destino)
            for origen in root.glob("*.csv"):
                self.assertEqual(origen.read_bytes(), (destino / origen.name).read_bytes())
            with self.assertRaises(FileExistsError):
                guardar_snapshot(root, destino)


if __name__ == "__main__":
    unittest.main()
