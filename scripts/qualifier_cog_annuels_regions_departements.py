#!/usr/bin/env python3
"""Contrôler les couches SIG annuelles contre les listes du COG Insee de la même année.

2018 : Insee TXT Latin-1/tabulation ; 2019 et après : ZIP de CSV UTF-8.
2017 et 2020 ne sont pas couverts par CET audit géométrique.
Aucune sortie dans docs/, aucun nouvel ARK, aucune création d'autorité.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import unicodedata
import zipfile
from pathlib import Path

ANNEES = (2018, 2019, 2021, 2022, 2023, 2024, 2025)
NIVEAUX = ("regions", "departements")
HORS_ECHELON = frozenset(("975", "977", "978", "984", "986", "987", "988", "989"))
SOURCE_PAGES = {
    2018: "https://www.insee.fr/fr/information/3363419",
    2019: "https://www.insee.fr/fr/information/3720946",
    2021: "https://www.insee.fr/fr/information/5057840",
    2022: "https://www.insee.fr/fr/information/6051727",
    2023: "https://www.insee.fr/fr/information/6800675",
    2024: "https://www.insee.fr/fr/information/7766585",
    2025: "https://www.insee.fr/fr/information/8377162",
}
# Les empreintes sont fixées seulement après contrôle des ZIP Insee authentiques.
ARCHIVES_SHA256 = {}

def empreinte(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def normaliser(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s).casefold())
    return re.sub(r"[^a-z0-9]+", " ",
                  "".join(c for c in s if not unicodedata.combining(c))).strip()

def membre_cog(archive: zipfile.ZipFile, annee: int, niveau: str) -> str:
    if annee == 2018:
        nom = ("reg2018.txt" if niveau == "regions" else "depts2018.txt")
        exact = [x for x in archive.namelist() if Path(x).name.lower() == nom]
    else:
        # Identifier le fichier de liste, pas un fichier des mouvements.
        motif = (r"(?:v_)?region[_-]?\d{4}\.csv$" if niveau == "regions"
                 else r"(?:v_)?departement[_-]?\d{4}\.csv$")
        exact = [x for x in archive.namelist()
                 if re.fullmatch(motif, Path(x).name.lower())]
    if len(exact) != 1:
        raise ValueError(f"Archive COG {annee}/{niveau} : membre ambigu/absent : {exact}")
    return exact[0]

def lire_cog(path: Path, annee: int, niveau: str) -> tuple[dict, dict]:
    brut = path.read_bytes()
    if not zipfile.is_zipfile(path):
        raise ValueError("Archive Insee non ZIP : "+str(path))
    h = empreinte(brut)
    if path.name in ARCHIVES_SHA256 and h != ARCHIVES_SHA256[path.name]:
        raise ValueError("Empreinte COG annuelle différente de la source validée : "+path.name)
    with zipfile.ZipFile(io.BytesIO(brut)) as archive:
        membre = membre_cog(archive, annee, niveau)
        content = archive.read(membre)
    texte = content.decode("latin-1" if annee == 2018 else "utf-8-sig")
    reader = csv.DictReader(io.StringIO(texte),
                            delimiter="\t" if annee == 2018 else ",")
    # 2019 diffuse des en-têtes minuscules ; les millésimes suivants passent
    # en majuscules, sans que les champs changent de signification.
    rows = [{str(k).upper(): v for k, v in r.items()} for r in reader]
    cle = ("REGION" if annee == 2018 else "REG") if niveau == "regions" else "DEP"
    parent = ("REGION" if annee == 2018 else "REG") if niveau == "departements" else None
    attendu = {cle, "NCCENR"} | ({parent} if parent else set())
    if not rows or not attendu.issubset(rows[0]):
        raise ValueError(f"Colonnes COG {annee}/{niveau} incorrectes : {list(rows[0]) if rows else 'vide'}")
    result = {}
    for row in rows:
        code = (row.get(cle) or "").strip()
        if not code or code in result:
            raise ValueError(f"Code vide ou dupliqué {annee}/{niveau}/{code}")
        nom = ((row.get("LIBELLE") if annee > 2018 else None)
               or row.get("NCCENR") or "").strip()
        if not nom:
            raise ValueError(f"Libellé vide {annee}/{niveau}/{code}")
        result[code] = {"nom": nom, "region": row[parent].strip() if parent else None}
    attendu_nombre = 18 if niveau == "regions" else 101
    if len(result) != attendu_nombre:
        raise ValueError(f"Cardinalité COG {annee}/{niveau}: {len(result)} ≠ {attendu_nombre}")
    return result, {"archive": path.name, "sha256": h, "membre": membre,
                    "membre_sha256": empreinte(content),
                    "page_insee": SOURCE_PAGES[annee]}

def lire_geo(racine: Path, annee: int, niveau: str) -> dict:
    chemin = racine / f"{niveau}-{annee}.geojson.gz"
    brut = chemin.read_bytes()
    texte = gzip.decompress(brut) if brut.startswith(b"\x1f\x8b") else brut
    d = json.loads(texte)
    if d.get("type") != "FeatureCollection":
        raise ValueError("Archive cartographique invalide : "+str(chemin))
    result = {}
    for feature in d.get("features", []):
        p = feature.get("properties") or {}
        code = str(p.get("code") or "")
        if not code or code in result:
            raise ValueError("Code géométrique vide ou dupliqué : "+str(chemin)+"/"+code)
        if code in HORS_ECHELON:
            continue
        result[code] = {"nom": p.get("nom") or "",
                        "region": p.get("region")}
    return result

def qualifier(archives_cog: Path, archives_geo: Path, sortie: Path) -> dict:
    if "docs" in sortie.resolve().parts:
        raise ValueError("Sortie publique interdite : audit de recette")
    if sortie.exists():
        raise ValueError("Refus de remplacer le rapport existant")
    rapport = {"schema": "adlfi.lieux.cog-annuels-2018-2025.v1",
               "statut": "RECETTE_COG_ANNUEL_SANS_PUBLICATION",
               "sources": SOURCE_PAGES,
               "nouvelles_autorites_pactols": 0, "millésimes": {}}
    for annee in ANNEES:
        rows = {}
        for niveau in NIVEAUX:
            fichier = (f"{niveau}-2018-txt.zip" if annee == 2018 else
                       f"cog_ensemble_{annee}_csv.zip")
            source = archives_cog / fichier
            cog, meta = lire_cog(source, annee, niveau)
            geo = lire_geo(archives_geo, annee, niveau)
            codes_cog, codes_geo = set(cog), set(geo)
            if codes_cog != codes_geo:
                raise ValueError(f"Codes géographiques/Cog différents {annee}/{niveau}:"
                                 f" non_cartographiés={sorted(codes_cog-codes_geo)}"
                                 f" sans_COG={sorted(codes_geo-codes_cog)}")
            divergences = []
            for code in sorted(cog):
                expected, measured = cog[code], geo[code]
                if niveau == "departements" and expected["region"] != measured["region"]:
                    raise ValueError(f"Rattachement départemental différent {annee}/{code}:"
                                     f" {expected['region']} / {measured['region']}")
                if normaliser(expected["nom"]) != normaliser(measured["nom"]):
                    divergences.append({
                        "code": code, "nom_COG": expected["nom"],
                        "nom_archive_SIG": measured["nom"]})
            rows[niveau] = {"nombre_codes": len(cog),
                            "divergences_de_libellé": divergences,
                            "source_COG": meta}
        rapport["millésimes"][str(annee)] = rows
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(json.dumps(rapport, ensure_ascii=False, indent=2, sort_keys=True)+"\n",
                      encoding="utf-8")
    return rapport

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archives-cog", required=True, type=Path)
    p.add_argument("--archives-geo", required=True, type=Path)
    p.add_argument("--sortie", required=True, type=Path)
    args = p.parse_args()
    result = qualifier(args.archives_cog, args.archives_geo, args.sortie)
    print(json.dumps({y: {n: {"effectif": v["nombre_codes"],
                               "noms_differents": len(v["divergences_de_libellé"])}
                           for n,v in layers.items()}
                      for y,layers in result["millésimes"].items()},
                     ensure_ascii=False))
