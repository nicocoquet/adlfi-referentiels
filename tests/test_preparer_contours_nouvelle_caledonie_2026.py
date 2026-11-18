"""Tests synthétiques de la recette néo-calédonienne : pas de publication implicite."""
import importlib.util
from pathlib import Path
import unittest
from shapely.geometry import Polygon, mapping

SPEC = importlib.util.spec_from_file_location(
    "nc", Path(__file__).resolve().parents[1] / "scripts/preparer_contours_nouvelle_caledonie_2026.py")
nc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(nc)

def fixtures():
    lines = [f"988{i:02d}|Commune {i}" for i in range(1, 34)]
    source = {"type": "FeatureCollection", "features": []}
    for i in range(1, 34):
        code = f"988{i:02d}"
        if code == "98805":
            geometry = mapping(Polygon([(165, -22), (166, -21), (165, -21), (166, -22), (165, -22)]))
        else:
            x, y = 165 + i / 100, -23 + i / 100
            geometry = mapping(Polygon([(x, y), (x+0.001, y), (x+0.001, y+0.001), (x, y)]))
        source["features"].append({"type": "Feature", "properties": {"code": code}, "geometry": geometry})
    index = {"schema": "adlfi.lieux.recherche.outremer.public.v1", "cog_ref": "2026-01-01",
             "contours_invalides": ["98745", "98805"], "communes": {"988": "\n".join(lines)}}
    return source, index

def test_32_valides_et_dumbea_exclue():
    source, index = fixtures()
    output = nc.preparer(source, index)
    codes = [f["properties"]["code"] for f in output["features"]]
    assert len(codes) == 32 and "98805" not in codes
    assert output["provenance"]["exclusion"]["code"] == "98805"
    assert all(f["properties"]["ark_pactols"] is None for f in output["features"])
    assert all(f["properties"]["limite_juridique_homologuee"] is False for f in output["features"])

def test_source_modifiee_refusee():
    source, index = fixtures()
    source["features"].pop()
    with unittest.TestCase().assertRaisesRegex(ValueError, "incomplète"):
        nc.preparer(source, index)

def test_anomalie_disparue_impose_nouvel_examen():
    source, index = fixtures()
    source["features"][4]["geometry"] = source["features"][3]["geometry"]
    with unittest.TestCase().assertRaisesRegex(ValueError, "nouvelle instruction"):
        nc.preparer(source, index)

def test_index_altere_refuse():
    source, index = fixtures()
    index["contours_invalides"] = []
    with unittest.TestCase().assertRaisesRegex(ValueError, "Signalements"):
        nc.preparer(source, index)
