#!/usr/bin/env python3
"""Tests d'intégration sur les vrais CSV COG 2026 et contours en recette."""
import argparse
import json
from pathlib import Path

def lire(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def actif(d,code,date):
    return [x["libelle"] for x in d["periodes_com"] if x["typecom"]=="COM"
            and x["code_insee"]==code and x["debut_inclus"]<=date
            and (not x["fin_exclue"] or date<x["fin_exclue"])]

def verifier(root):
    root=Path(root)
    manifest=lire(root/"manifest.json")
    assert manifest["statut"]=="recette_pour_revision_avant_pages"
    for reg in ("bfc","pdl","corse","paca"):
        d=lire(root/("cog-"+reg+".json"))
        g=lire(root/("contours-2026-"+reg+".geojson"))
        assert d["region"]==reg and d["geometries_historiques"]==[]
        assert g["provenance"]["millesime"]==2026
        assert len(g["features"])==manifest["regions"][reg]["contours_2026"]
        codes=[x["properties"]["code"] for x in g["features"]]
        assert len(codes)==len(set(codes))
        assert all(x["properties"]["millesime"]==2026 for x in g["features"])
        assert all(x["properties"]["ark_pactols_valide_2026"] is None
                   for x in g["features"]) if reg!="paca" else True
        assert not d["alignements_Pactols_COG_valides_2026"] if reg!="paca" else True
    bfc=lire(root/"cog-bfc.json")
    pdl=lire(root/"cog-pdl.json")
    corse=lire(root/"cog-corse.json")
    paca=lire(root/"cog-paca.json")
    assert actif(bfc,"25368","2017-01-01")==["Marchaux"]
    assert actif(bfc,"25368","2018-01-01")==["Marchaux-Chaudefontaine"]
    assert actif(bfc,"39137","2018-01-01")==["Chemilla"]
    assert actif(bfc,"39137","2019-01-01")==["Saint-Hymetière-sur-Valouse"]
    assert actif(bfc,"71566","2024-01-01")==["Verdun-sur-le-Doubs"]
    assert actif(bfc,"71566","2025-01-01")==["Verdun-Ciel"]
    assert actif(pdl,"49069","2024-01-01")==["Orée d'Anjou"]
    assert actif(pdl,"49069","2026-01-01")==[]
    assert actif(pdl,"49126","2026-01-01")==["Orée d'Anjou"]
    assert any(x["code_insee"]=="49069" and x["typecom"]=="COMD" and
               x["comparent_2026"]=="49126"
               for x in pdl["observations_COMA_COMD_2026"])
    assert any(x["mod"]=="41" and x["date_effet"]=="1976-01-01"
               and x["code_avant"].startswith("20")
               for x in corse["lignes_mouvements_cog"])
    assert len(paca["alignements_Pactols_COG_valides_2026"])==103
    assert all(x["millesime_validation"]==2026
               for x in paca["alignements_Pactols_COG_valides_2026"])
    assert sum(len(lire(root/("cog-"+r+".json"))["geometries_historiques"])
               for r in ("bfc","pdl","corse","paca"))==0
    print("Lieux : quatre régions COG réelles, 103 validations PACA, transitions et contours 2026 OK")
    return manifest["regions"]

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("dossier",type=Path)
    print(verifier(p.parse_args().dossier))
