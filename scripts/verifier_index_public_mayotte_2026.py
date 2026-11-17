#!/usr/bin/env python3
"""Contrôler les 34 épisodes Mayotte COMER/DROM contre les CSV Insee COG 2026.

Les 17 communes restent distinguées de la collectivité 976D puis 976R ;
ne jamais interpréter le 31 mars 2011 comme date de création communale.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

SHAS = {
    "v_commune_outremer_depuis_1943.csv": "d2e2d3b376540d5c5e624e1cdf3d6a1959f6f24d6763268eec67883fe82ce748",
    "v_commune_depuis_1943.csv": "08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee",
    "v_commune_2026.csv": "7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3",
}
CODES = {f"976{i:02d}" for i in range(1, 18)}

def empreinte(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def lire(p: Path) -> list[dict]:
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        first = f.readline()
        f.seek(0)
        sep = ";" if first.count(";") > first.count(",") else ","
        rdr = csv.DictReader(f, delimiter=sep)
        rows = list(rdr)
    if not rows or any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError("CSV COG manquant ou altéré : " + p.name)
    return rows

def verifier(cog: Path, public: dict) -> dict:
    for name, sha in SHAS.items():
        if empreinte(cog / name) != sha:
            raise ValueError("SHA-256 du COG officiel incompatible : " + name)
    if public.get("schema") != "adlfi.lieux.mayotte.etats_cog_public.v1":
        raise ValueError("Schéma d'historique public Mayotte absent")
    if public["cog_comer_historique_sha256"] != SHAS["v_commune_outremer_depuis_1943.csv"] or (
       public["cog_drom_historique_sha256"] != SHAS["v_commune_depuis_1943.csv"]) or (
       public["cog_communes_2026_sha256"] != SHAS["v_commune_2026.csv"]):
        raise ValueError("Provenance de l'index public incompatible")
    current = {
        x["COM"]: x["LIBELLE"] for x in lire(cog / "v_commune_2026.csv")
        if x["TYPECOM"] == "COM" and x["DEP"] == "976"
    }
    if set(current) != CODES:
        raise ValueError("17 communes actuelles COG Mayotte attendues")
    comer = sorted(
        (x["COM_COMER"], x["LIBELLE"], "COMER", x["DATE_DEBUT"], x["DATE_FIN"])
        for x in lire(cog / "v_commune_outremer_depuis_1943.csv")
        if x["NATURE_ZONAGE"] == "COM" and x["COM_COMER"] in CODES
    )
    drom = sorted(
        (x["COM"], x["LIBELLE"], "DROM", x["DATE_DEBUT"], x["DATE_FIN"])
        for x in lire(cog / "v_commune_depuis_1943.csv")
        if x["TYPECOM"] == "COM" and x["COM"] in CODES
    )
    if len(comer) != len(drom) or len(comer) != 17:
        raise ValueError("Les deux séries historiques Mayotte doivent couvrir 17 codes")
    public_rows = sorted(tuple(line.split("|")) for line in public["episodes"].splitlines())
    if sorted(comer + drom) != public_rows:
        raise ValueError("Épisodes publics discordants des tables COG officielles")
    bycode = collections.defaultdict(list)
    for item in public_rows:
        if len(item) != 5:
            raise ValueError("Épisode Mayotte mal formé")
        bycode[item[0]].append(item)
    for code in CODES:
        rows = sorted(bycode[code], key=lambda x:x[3])
        if len(rows) != 2 or rows[0] != (code,current[code],"COMER","2007-02-23","2011-03-31") or (
           rows[1] != (code,current[code],"DROM","2011-03-31","")):
            raise ValueError("Continuité de code et nom Mayotte non attestée : "+code)
    t = public["transition_famille_cog"]
    if t["date_effet"] != "2011-03-31" or t["avant"] != "COMER" or (
       t["apres"] != "DROM") or t["codes_communes_conserves"] != 17 or (
       t["date_creation_des_communes"] is not None) or (
       t["creation_de_communes_par_cette_transition"] is not False):
        raise ValueError("Transition de statut faussement présentée comme création")
    collector = public["collectivite_statut_particulier"]
    if collector["code_2011_2025"] != "976D" or (
       collector["code_2026"] != "976R") or collector["date_effet_code_2026"] != "2026-01-01":
        raise ValueError("Code de collectivité Mayotte incomplet ou confondu")
    ark=public["ark_confirme_sans_alignement_valide"]
    if ark != {"code":"97607","ark":"26678/crtZcuFSJVYZU"} or (
       public["correspondances_pactols_COG_2026_conservees"] != 16) or (
       any(public[k] != 0 for k in ("nouveaux_alignements_pactols",
            "contours_historiques_publies","nouvelles_relations_successions_inferrees"))):
        raise ValueError("Réserve éditoriale Pactols / absence de contours historiques violée")
    return {
        "codes_actuels":17,"episodes_COMER":17,"episodes_DROM":17,
        "total_episodes":34,"transition_statut":"2011-03-31",
        "correspondances_validees_2026_conservees":16,
        "ark_non_aligne":"26678/crtZcuFSJVYZU",
        "geometries_historiques_publiees":0
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cog-dir",type=Path,required=True)
    parser.add_argument("--public",type=Path,required=True)
    args=parser.parse_args()
    data=json.loads(args.public.read_text(encoding="utf-8"))
    print(json.dumps(verifier(args.cog_dir,data),ensure_ascii=False,indent=2,sort_keys=True))
