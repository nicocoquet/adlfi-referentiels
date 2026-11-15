#!/usr/bin/env python3
"""Audit des régions, rattachements départementaux et fusions COG 2015/2016/2026.

Source : fichiers officiels Insee ; instantané, NON historique continu.
La relation de fusion (01/01/2016) est codée d'après la loi n°2015-29,
article 1, et contrôlée sur les listes régionales et départementales.
Aucune géométrie historique ni correspondance Pactols n'est attribuée.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

HASHES = {
    "reg2015": "f943f206fbc4d2d2766738a66169e3788a0c1e42b9fbed637d728fc6c76ba227",
    "reg2016": "60a15fe2d5cb74ca8c8cb07f0464d360c2f9faa051fa8ee21c2a2a47e35199ea",
    "reg2026": "d903566d9c0d263389d279baea6761917b7460749a07bec8ba37dd8f2ff7d98a",
    "dep2015": "67ad93d56606e2b48e3560ca35de70abaea1ed267feb5519204daa0a2cdbc1f6",
    "dep2016": "d8426f9d13e11638a04eb67d27d9b23396a92e510dbd42fabe68974e177c8ac8",
    "dep2026": "513900ca23edc682ef9b912d7bfc317129eac3a7d71ff19bc22b40ea4838e6eb",
}
FUSIONS_2016 = {
    "27": ("26", "43"),                  # Bourgogne + Franche-Comté
    "28": ("23", "25"),                  # Haute + Basse-Normandie
    "32": ("22", "31"),                  # Picardie + Nord-Pas-de-Calais
    "44": ("21", "41", "42"),            # Champagne-Ardenne + Lorraine + Alsace
    "75": ("54", "72", "74"),            # Poitou-Charentes + Aquitaine + Limousin
    "76": ("73", "91"),                  # Midi-Pyrénées + Languedoc-Roussillon
    "84": ("82", "83"),                  # Rhône-Alpes + Auvergne
}
INSEE_2015 = "https://www.insee.fr/fr/information/2560698"
INSEE_2016 = "https://www.insee.fr/fr/information/2114819"
INSEE_2026 = "https://www.insee.fr/fr/information/8740222"
LOI = "https://www.legifrance.gouv.fr/eli/loi/2015/1/16/INTX1412841L/jo/article_1"
FILES = {
    "reg2015": "reg2015.txt", "reg2016": "reg2016.txt",
    "dep2015": "depts2015.txt", "dep2016": "depts2016.txt"
}
OUTPUTS = {
    "snap": "regions_millesimes_2015_2016_2026.csv",
    "fus": "successions_regionales_2016.csv",
    "dep": "appartenances_departement_region_millesimes.csv",
    "ren": "changements_libelles_regions_2016_2026.csv",
    "report": "rapport_region_2015_2016_2026.json",
}

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def csv_lire(path: Path, kind: str, year: int) -> list[dict]:
    if year < 2026:
        with zipfile.ZipFile(path) as z:
            names = [n for n in z.namelist() if n.lower().endswith(".txt")]
            if names != [FILES[f"{kind}{year}"]]:
                raise ValueError(f"Fichier d'archive Insee inattendu : {names}")
            b = z.read(names[0])
        # Insee COG 2015/2016 archives : TAB et Latin-1 effectivement vérifiés.
        text = b.decode("latin-1")
        delimiter = "\t"
        expected = ({"REGION", "CHEFLIEU", "TNCC", "NCC", "NCCENR"} if kind == "reg"
                    else {"REGION", "DEP", "CHEFLIEU", "TNCC", "NCC", "NCCENR"})
    else:
        text = Path(path).read_text(encoding="utf-8-sig")
        delimiter = ","
        expected = ({"REG", "CHEFLIEU", "NCCENR", "LIBELLE"} if kind == "reg"
                    else {"DEP", "REG", "CHEFLIEU", "NCCENR", "LIBELLE"})
    rd = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    if not expected.issubset(rd.fieldnames or []):
        raise ValueError(f"En-têtes {kind} {year} incorrects : {rd.fieldnames}")
    records = list(rd)
    if any(not r.get("NCCENR", "").strip() for r in records):
        raise ValueError(f"Libellé manquant {kind} {year}")
    return records

def analyser(sources: dict[str, Path], strict: bool = True) -> dict:
    if set(sources) != set(HASHES):
        raise ValueError("Six sources Insee requises")
    hashes = {role: sha256(path) for role, path in sources.items()}
    if strict and hashes != HASHES:
        raise ValueError("Empreintes officielles inattendues : vérifier les fichiers et millésimes")
    regions = {y: csv_lire(sources[f"reg{y}"], "reg", y) for y in (2015, 2016, 2026)}
    depts = {y: csv_lire(sources[f"dep{y}"], "dep", y) for y in (2015, 2016, 2026)}
    regs = {y: {r["REGION" if y < 2026 else "REG"]: r for r in regions[y]}
            for y in regions}
    depidx = {y: {r["DEP"]: r for r in depts[y]} for y in depts}
    if strict:
        for y, n in ((2015, 27), (2016, 18), (2026, 18)):
            if len(regs[y]) != n or len(regions[y]) != n:
                raise ValueError(f"Effectif régions {y} incompatible : {len(regions[y])}")
            if len(depidx[y]) != 101 or len(depts[y]) != 101:
                raise ValueError(f"Effectif départements {y} incompatible")
    if set(regs[2016]) != set(regs[2026]):
        raise ValueError("Codes régionaux 2016 / 2026 divergents : instruction supplémentaire")
    if set(depidx[2015]) != set(depidx[2016]) or set(depidx[2016]) != set(depidx[2026]):
        raise ValueError("Ensemble des codes départementaux divergents")
    merged_old = {code for old in FUSIONS_2016.values() for code in old}
    if len(merged_old) != 16 or len(FUSIONS_2016) != 7:
        raise ValueError("Sept fusions et 16 anciennes régions attendues")
    old_to_new = {}
    for successor, old_codes in FUSIONS_2016.items():
        if successor in regs[2015] or successor not in regs[2016]:
            raise ValueError("Code cible de fusion erroné : " + successor)
        for code in old_codes:
            if code in old_to_new or code not in regs[2015]:
                raise ValueError("Ancien code absent/dupliqué : " + code)
            old_to_new[code] = successor
    for code in regs[2015]:
        if code not in old_to_new:
            if code not in regs[2016]:
                raise ValueError("Ancienne région sans successeur documenté : " + code)
            old_to_new[code] = code
    if len(old_to_new) != len(regs[2015]):
        raise ValueError("Relation régionale incomplète")

    snapshots = [
        {"millesime":str(y), "date_reference":f"{y}-01-01", "code_reg":code,
         "libelle":r.get("LIBELLE",r["NCCENR"]), "nccenr":r["NCCENR"],
         "chef_lieu_cog":r["CHEFLIEU"], "source":INSEE_2026 if y == 2026
         else INSEE_2015 if y == 2015 else INSEE_2016,
         "statut":"instantane_COG_non_periode_continue"}
        for y in (2015,2016,2026)
        for code,r in sorted(regs[y].items())
    ]
    successions = [
        {"evenement":"reorganisation_2016", "date_effet":"2016-01-01",
         "code_reg_avant":code,
         "libelle_reg_avant":regs[2015][code]["NCCENR"],
         "code_reg_apres":old_to_new[code],
         "libelle_reg_apres_COG2016":regs[2016][old_to_new[code]]["NCCENR"],
         "type_relation":"fusion" if code in merged_old else "continuite_code",
         "nombre_predecesseurs":sum(v == old_to_new[code] for v in old_to_new.values()),
         "preuve":LOI if code in merged_old else INSEE_2015+" ; "+INSEE_2016,
         "decision":"relation_COG_historique_non_alignee_Pactols"}
        for code in sorted(regs[2015])
    ]
    appart = []
    departements_modifies = 0
    for dep in sorted(depidx[2015]):
        a, b, c = (depidx[y][dep] for y in (2015, 2016, 2026))
        ca, cb, cc = a["REGION"], b["REGION"], c["REG"]
        if old_to_new[ca] != cb:
            raise ValueError(f"Changement d'appartenance départementale non couvert par la loi : {dep}: {ca}->{cb}")
        if cb != cc:
            raise ValueError(f"Changement de région entre 2016 et 2026 non instruit : {dep}: {cb}->{cc}")
        if ca != cb:
            departements_modifies += 1
        for y, row in ((2015,a),(2016,b),(2026,c)):
            reg = row["REGION" if y < 2026 else "REG"]
            if reg not in regs[y]:
                raise ValueError(f"Région parente absente {dep} : {reg}")
            appart.append({
                "millesime":str(y), "code_dep":dep, "libelle_dep":row["NCCENR"],
                "code_reg_parent":reg, "libelle_reg_parent":regs[y][reg]["NCCENR"],
                "date_reference":f"{y}-01-01",
                "statut":"appartenance_COG_au_millesime_non_periode_continue",
            })
    if strict and departements_modifies != 65:
        raise ValueError(f"65 départements devraient changer de code régional, trouvé : {departements_modifies}")
    names_changed = [
        {"code_reg":code, "libelle_COG2016":regs[2016][code]["NCCENR"],
         "libelle_COG2026":regs[2026][code]["NCCENR"],
         "date_effet_changement":"A_INSTRUIRE",
         "preuve":"comparaison_COG_2016_2026_non_date_exacte"}
        for code in sorted(regs[2026])
        if regs[2016][code]["NCCENR"] != regs[2026][code]["NCCENR"]
    ]
    if strict and set(r["code_reg"] for r in names_changed) != {"32","44","75","76"}:
        raise ValueError("Les quatre changements de libellé de 2016 à 2026 diffèrent")
    status = {
        "schema":"adlfi.lieux.regions_cog.audit_millesimes.v1",
        "statut":"RECETTE_NON_VALIDANTE_HORS_PAGES",
        "annees":{str(y):{"regions":len(regions[y]),"departements":len(depts[y])}
                  for y in (2015,2016,2026)},
        "fusions_regionales_2016":len(FUSIONS_2016),
        "anciennes_regions_fusionnees":len(merged_old),
        "regions_ancien_millesime_reliees":len(old_to_new),
        "departements_reg_2015_differente_2016":departements_modifies,
        "departements_reg_2016_differente_2026":0,
        "libelles_2016_2026_differents":names_changed,
        "sources_sha256":hashes,
        "alignements_pactols_crees":0,
        "geometries_historiques_creees":0,
        "avertissements":[
            "Un COG annuel atteste la situation au 1er janvier, pas toute une période.",
            "Les libellés provisoires de 2016 ne sont pas les noms officiels de 2026.",
            "Un code inchangé ne prouve pas la stabilité juridique ni géométrique.",
            "Les COMER ne sont pas des régions et n'entrent pas dans la liste régionale.",
            "Une nouvelle région issue d'une fusion a plusieurs prédécesseurs explicites.",
            "Aucune géométrie contemporaine n'est projetée dans le passé.",
        ],
    }
    return {"regions":snapshots,"successions":successions,
            "appartenances":appart,"renommages":names_changed,"rapport":status}

def ecrire(result:dict, out:Path):
    out=Path(out)
    if "docs" in out.resolve().parts:
        raise ValueError("Sortie de recette impossible dans docs/")
    out.mkdir(parents=True,exist_ok=True)
    for key in ("snap","fus","dep","ren"):
        field={"snap":"regions","fus":"successions",
               "dep":"appartenances","ren":"renommages"}[key]
        rows=result[field]
        with (out/OUTPUTS[key]).open("w",encoding="utf-8-sig",newline="") as f:
            cols=list(rows[0]) if rows else (
                ["code_reg","libelle_COG2016","libelle_COG2026","date_effet_changement","preuve"])
            w=csv.DictWriter(f,fieldnames=cols,delimiter=";")
            w.writeheader();w.writerows(rows)
    (out/OUTPUTS["report"]).write_text(
        json.dumps(result["rapport"],ensure_ascii=False,indent=2,sort_keys=True)+"\n",
        encoding="utf-8")

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for role in HASHES:
        p.add_argument("--"+role,required=True,type=Path)
    p.add_argument("--sortie",required=True,type=Path)
    a=vars(p.parse_args())
    out=a.pop("sortie")
    report=analyser(a)
    ecrire(report,out)
    print(json.dumps(report["rapport"],ensure_ascii=False,indent=2))
