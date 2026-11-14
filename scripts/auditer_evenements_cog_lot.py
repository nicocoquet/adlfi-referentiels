#!/usr/bin/env python3
"""Audit non validant des événements communaux du COG 2026 pour un lot Pactols."""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import re
import unicodedata
from pathlib import Path

HEAD_LOT = {"ark_pactols", "libelle_documentaire", "codes_cog_departement_concordants", "details_cog_candidats"}
HEAD_MVT = {"MOD", "DATE_EFF", "TYPECOM_AV", "COM_AV", "LIBELLE_AV", "TYPECOM_AP", "COM_AP", "LIBELLE_AP"}
MODS = {
    "10":"Changement de nom", "20":"Création", "21":"Rétablissement",
    "30":"Suppression", "31":"Fusion simple", "32":"Création de commune nouvelle",
    "33":"Fusion association", "34":"Transformation de fusion association en fusion simple",
    "35":"Suppression de commune déléguée",
    "41":"Changement de code dû à un changement de département",
    "50":"Changement de code dû à un transfert de chef-lieu",
    "70":"Transformation de commune associée en commune déléguée",
    "71":"Rétablissement de commune déléguée", "72":"Création de commune déléguée",
}

def lire_csv(path: Path, colonnes: set[str]) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        premiere_ligne=fh.readline()
        separateur=";" if premiere_ligne.count(";") > premiere_ligne.count(",") else ","
        fh.seek(0)
        reader=csv.DictReader(fh, delimiter=separateur)
        manquantes=colonnes-set(reader.fieldnames or [])
        if manquantes:
            raise ValueError(f"{path}: colonnes manquantes {sorted(manquantes)}")
        return list(reader)

def normaliser(text: str) -> str:
    text=text.replace("œ","oe").replace("Œ","Oe")
    return " ".join(re.sub("[^a-z0-9]+"," ","".join(
        c for c in unicodedata.normalize("NFKD",text.casefold())
        if not unicodedata.combining(c))).split())

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def transitions_probables(lot: list[dict]) -> list[dict]:
    result=[]
    for row in lot:
        codes=json.loads(row["codes_cog_departement_concordants"])
        historique=json.loads(row["details_cog_candidats"])
        if len(codes)!=1:
            continue
        apres=[x for x in historique if x["code_insee_historique"]==codes[0]]
        anciens=[x for x in historique if x["code_insee_historique"]!=codes[0]]
        for a in anciens:
            for b in apres:
                if a["date_fin"] and a["date_fin"]==b["date_debut"] and normaliser(a["libelle_cog"])==normaliser(b["libelle_cog"]):
                    result.append({
                        "ark_pactols":row["ark_pactols"],
                        "libelle_documentaire":row["libelle_documentaire"],
                        "code_avant":a["code_insee_historique"],
                        "code_apres":codes[0],
                        "date_jointive":a["date_fin"],
                    })
    return result

def auditer(lot_csv: Path, mvt_csv: Path, sortie: Path) -> dict:
    sources=(lot_csv,mvt_csv)
    for source in sources:
        if not source.is_file():
            raise FileNotFoundError(source)
    lot=lire_csv(lot_csv, HEAD_LOT)
    mvts=lire_csv(mvt_csv, HEAD_MVT)
    transitions=transitions_probables(lot)
    index=collections.defaultdict(list)
    for m in mvts:
        index[m["COM_AV"]].append(m)
    revue=[]
    for t in transitions:
        matching=[m for m in index[t["code_avant"]]
                  if m["COM_AP"]==t["code_apres"] and m["DATE_EFF"]==t["date_jointive"]]
        mods=sorted(set(m["MOD"] for m in matching))
        revue.append({
            **t,
            "nombre_evenements_exacts":len(matching),
            "codes_MOD":"|".join(mods),
            "libelles_MOD":"|".join(MODS.get(mod, "Code inconnu "+mod) for mod in mods),
            "statut_preuve":"mouvement_cog_direct_atteste" if matching else "mouvement_exact_non_retrouve",
            "statut_validation_pactols":"non_valide",
            "preuve_lignes_cog":json.dumps(matching,ensure_ascii=False),
        })
    particuliers=[]
    dossiers=[("Allaines-Mervilliers",{"28002","28199"}),("Aigondigné",{"79185","79004","79327","79240"})]
    for nom,codes in dossiers:
        candidats=[r["ark_pactols"] for r in lot if r["libelle_documentaire"]==nom]
        if not candidats:
            continue
        for m in mvts:
            if not (m["COM_AV"] in codes or m["COM_AP"] in codes):
                continue
            if not (m["DATE_EFF"].startswith("2019") or (nom=="Aigondigné" and m["DATE_EFF"].startswith("2017"))):
                continue
            particuliers.append({
                "dossier":nom,"ark_pactols":candidats[0],
                **{k:m.get(k,"") for k in ("DATE_EFF","MOD","TYPECOM_AV","COM_AV","LIBELLE_AV","TYPECOM_AP","COM_AP","LIBELLE_AP")},
                "sens_evenement":MODS.get(m["MOD"],"Code inconnu"),
                "statut_validation_pactols":"non_valide",
            })
    destinations=[sortie/n for n in ("transitions_code_a_verifier.csv","evenements_communaux_particuliers.csv","rapport_evenements_lot001.json")]
    if any(p.resolve() in {source.resolve() for source in sources} for p in destinations):
        raise ValueError("Une sortie écraserait une source")
    sortie.mkdir(parents=True, exist_ok=True)
    def exporter(nom,colonnes,donnees):
        with (sortie/nom).open("w",encoding="utf-8-sig",newline="") as fh:
            writer=csv.DictWriter(fh,delimiter=";",fieldnames=colonnes,extrasaction="ignore")
            writer.writeheader()
            writer.writerows(donnees)
    exporter("transitions_code_a_verifier.csv",[
        "ark_pactols","libelle_documentaire","code_avant","code_apres","date_jointive",
        "nombre_evenements_exacts","codes_MOD","libelles_MOD","statut_preuve",
        "statut_validation_pactols","preuve_lignes_cog"],revue)
    exporter("evenements_communaux_particuliers.csv",[
        "dossier","ark_pactols","DATE_EFF","MOD","sens_evenement",
        "TYPECOM_AV","COM_AV","LIBELLE_AV","TYPECOM_AP","COM_AP","LIBELLE_AP",
        "statut_validation_pactols"],particuliers)
    repartition=collections.Counter(mod for r in revue for mod in r["codes_MOD"].split("|") if mod)
    rapport={
        "schema_version":"0.1.0","etat":"audit_evenements_non_validant",
        "autorites_lot":len(lot),"lignes_evenements_source":len(mvts),
        "transitions_codes_candidats":len(revue),
        "transitions_avec_evenement_direct_exact":sum(bool(x["nombre_evenements_exacts"]) for x in revue),
        "transitions_sans_evenement_direct_exact":sum(not x["nombre_evenements_exacts"] for x in revue),
        "evenements_cog_releves_pour_deux_dossiers_speciaux":len(particuliers),
        "repartition_MOD_transitions":dict(sorted(repartition.items())),
        "sources":{p.name:sha256(p) for p in sources},
        "avertissement":"Les événements attestent des mutations administratives, jamais une équivalence Pactols ou géométrique historique."
    }
    destinations[2].write_text(json.dumps(rapport,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return rapport

def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--lot",type=Path,required=True)
    cli.add_argument("--evenements",type=Path,required=True)
    cli.add_argument("--sortie",type=Path,required=True)
    args=cli.parse_args()
    print(json.dumps(auditer(args.lot,args.evenements,args.sortie),ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
