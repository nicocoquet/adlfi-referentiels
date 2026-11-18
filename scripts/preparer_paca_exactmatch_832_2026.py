#!/usr/bin/env python3
"""PACA : préflight exhaustif des URI INSEE des 832 candidats exactMatch 2026.

Sépare les 103 validations du pilote des nouveaux candidats. Ne publie aucun
ARK, état historique ni tracé. Un exactMatch à une URI INSEE de type UUID,
mal typée ou concurrente entraîne une mise en quarantaine explicite.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from auditer_paca_pactols_cog_2026 import audit
from auditer_pactols_polynesie_2026 import ARK, RDF, SKOS, RDF_SHA
from preparer_validations_pactols_corse_2026 import FIELDS, ecrire_csv

SCHEMA = "adlfi.lieux.paca.exactmatch.preflight.2026.v1"
GEO_PREFIX = re.compile(r"^https?://id\.insee\.fr/geo/", re.I)
# Les URIs de communes sous forme de code sont déjà recensées par l'audit.
STATUS = "CANDIDAT_CONFORME_EXACTMATCH_UNIVOQUE_PRE_PUBLICATION"

def scanner_toutes_uris(rdf: Path, selection: list[dict]) -> dict:
    """Retourne les URI INSEE, y compris UUID et chemins non reconnus."""
    attendus = {x["ark_pactols"]: x["uri_insee"] for x in selection}
    results = {}
    p = ET.iterparse(rdf, events=("start","end"))
    _,root = next(p)
    if root.tag != RDF+"RDF":
        raise ValueError("RDF inattendu")
    for event,el in p:
        if event != "end" or el.tag not in (SKOS+"Concept", RDF+"Description"):
            continue
        m = ARK.fullmatch(el.get(RDF+"about",""))
        if not m or m.group(1) not in attendus:
            el.clear();root.clear();continue
        ark=m.group(1)
        if ark in results:
            raise ValueError("Concept en double dans le RDF : "+ark)
        uris = sorted({x.get(RDF+"resource","") for x in el.findall(SKOS+"exactMatch")
                       if GEO_PREFIX.match(x.get(RDF+"resource",""))})
        expected=attendus[ark]
        results[ark]={"ark_pactols":ark,"uri_attendue":expected,
                      "toutes_uris_insee":uris,"preflight_uris":(
                          "CONFORME_UNE_URI_COG_2026" if uris==[expected]
                          else "URI_INSEE_SUPPLEMENTAIRE_OU_NON_RECONNUE")}
        el.clear();root.clear()
    if set(results)!=set(attendus):
        raise ValueError("ARK candidats absents du snapshot : "+str(sorted(set(attendus)-set(results))[:10]))
    return results

def preparer_depuis_rapport(rapport:dict) -> tuple[list[dict],list[dict],dict]:
    if rapport.get("schema") != "adlfi.lieux.paca.cog-pactols.2026.audit.v1":
        raise ValueError("Rapport PACA de source incorrecte")
    lignes=rapport["communes"]
    pilot=[x for x in lignes if x["pilote_103_valide"]]
    outside=[x for x in lignes if not x["pilote_103_valide"]]
    if len(lignes)!=946 or len(pilot)!=103 or len(outside)!=843:
        raise ValueError("Effectifs du pilote PACA ou COG divergents")
    if sum(x["statut_rdf"]=="ELIGIBLE_SELON_REGLE" for x in outside)!=832:
        raise ValueError("832 candidats attendus hors pilote, vérification éditoriale requise")
    pending=[]
    exceptions=[]
    ark_seen=set()
    for row in sorted(outside,key=lambda x:x["code"]):
        code=row["code"]
        if row["statut_rdf"]!="ELIGIBLE_SELON_REGLE":
            exceptions.append({"code_insee":code,"libelle_COG_2026":row["libelle"],
                               "ark_candidats":row["arks_exactMatch_dans_rdf"],
                               "statut":row["statut_rdf"],
                               "decision":"A_INSTRUIRE_SANS_PUBLICATION"})
            continue
        evidence=row["preuves_RDF_exactMatch"]
        if len(evidence)!=1 or len(evidence[0]["insee_exactMatch"])!=1:
            raise ValueError("Candidat non univoque : "+code)
        p=evidence[0]
        exact=p["insee_exactMatch"][0]
        if (exact["code"]!=code or exact["famille"]!="commune"
            or p["deprecie"] or p["remplace"] or len(p["prefLabels_fr"])!=1
            or len(p["codes_communaux_cites"])!=1 or p["ark"] in ark_seen):
            raise ValueError("Concept non éligible ou réutilisé : "+code)
        ark_seen.add(p["ark"])
        pending.append(dict(zip(FIELDS,(
            code,row["libelle"],"93",row["departement"],p["ark"],exact["uri"],
            "skos:exactMatch",p["prefLabels_fr"][0],
            rapport["sources"]["pactols"]["sha256"],STATUS,
            "2026-01-01","REGLE_EXACTMATCH_UNIVOQUE_AVEC_CONTROLE_URIS",
            "EN_ATTENTE_RECETTE_PUBLICATION",
        ))))
    if len(pending)!=832 or len(exceptions)!=11:
        raise ValueError("832 candidats et 11 exceptions attendus")
    if set(p["ark_pactols"] for p in pending)&set(x["ark_pilote"] for x in pilot):
        raise ValueError("Un ARK du pilote réemployé par un autre code")
    return pending,exceptions,{"pilote":pilot,"communes":lignes}

def qualifier(rdf:Path, rapport:dict) -> tuple[list[dict],dict]:
    selection,exceptions,meta=preparer_depuis_rapport(rapport)
    uris=scanner_toutes_uris(rdf,selection)
    valides=[]
    quarantaines=[]
    for row in selection:
        check=uris[row["ark_pactols"]]
        if check["preflight_uris"]=="CONFORME_UNE_URI_COG_2026":
            valides.append(row)
        else:
            quarantaines.append({
                "code_insee":row["code_insee"],"libelle_COG_2026":row["libelle_COG_2026"],
                **check,"decision":"A_INSTRUIRE_SANS_PUBLICATION"})
    if len(valides)+len(quarantaines)!=832:
        raise ValueError("Préflight incomplet")
    summary={
        "schema":SCHEMA,"statut":"PRE_PUBLICATION_SEULEMENT",
        "source_RDF_sha256":rapport["sources"]["pactols"]["sha256"],
        "source_RDF_commit":rapport["sources"]["pactols"]["commit"],
        "source_COG_sha256":rapport["sources"]["cog"]["sha256"],
        "date_COG":"2026-01-01",
        "bilan":{
            "communes_COG_PACA_2026":946,"pilotage_editeur_conserve":103,
            "pilote_devoluy_multiple_ARK":1,
            "candidats_eligibles_avant_preflight":832,
            "candidats_conformes_apres_preflight":len(valides),
            "candidats_mis_en_quarantaine_URI":len(quarantaines),
            "exceptions_paca_hors_pilote":len(exceptions),
            "nouvelles_relations_publiees":0,"geometries_modifiees":0,
            "relations_historiques_inferees":0,
        },
        "pilotage_valide_2026":sorted(
            [{"code_insee":x["code"],"ark_pactols":x["ark_pilote"],
              "decision":"CONSERVEE_VALIDATION_EDITEUR_2026",
              "eligibilite_RDF":x["statut_rdf"]}
             for x in meta["pilote"]],key=lambda x:x["code_insee"]),
        "exceptions_cog_pactols":exceptions,
        "quarantaines_URI_INSEE":quarantaines,
        "limites":[
            "L'exactMatch univoque vers le COG 2026 fonde uniquement une correspondance 2026.",
            "Le contrôle exhaustif des URI INSEE protège des UUID non reconnus et des URI concurrentes.",
            "La classification stricte peut exclure des ARK éditorialement validés (cas Dévoluy) : validation du pilote conservée.",
            "Aucun concept de lieu, mouvement COG ancien ou contour historique n'est généré.",
        ]
    }
    return valides,summary

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rdf",required=True,type=Path)
    p.add_argument("--cog",required=True,type=Path)
    p.add_argument("--pilote",required=True,type=Path)
    p.add_argument("--sortie-csv",required=True,type=Path)
    p.add_argument("--sortie-bilan",required=True,type=Path)
    a=p.parse_args()
    if a.sortie_csv.resolve()==a.sortie_bilan.resolve():
        raise ValueError("Sorties identiques")
    for path in (a.sortie_csv,a.sortie_bilan):
        if path.exists() or "docs" in path.resolve().parts:
            raise ValueError("Sortie neuve hors docs/")
    rapport=audit(a.rdf,a.cog,a.pilote)
    if hashlib.sha256(a.rdf.read_bytes()).hexdigest()!=RDF_SHA:
        raise ValueError("RDF non conforme")
    valid,summary=qualifier(a.rdf,rapport)
    ecrire_csv(valid,a.sortie_csv)
    a.sortie_bilan.parent.mkdir(parents=True,exist_ok=True)
    a.sortie_bilan.write_text(json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("PACA_PREFLIGHT_2026",json.dumps({
        **summary["bilan"],"sha256_csv":hashlib.sha256(a.sortie_csv.read_bytes()).hexdigest(),
        "sha256_rapport":hashlib.sha256(a.sortie_bilan.read_bytes()).hexdigest()
    },ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
