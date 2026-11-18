#!/usr/bin/env python3
"""Publication Pactols–COG PACA 2026 complémentaire des 103 autorités du pilote.

Le registre de 832 liens, le rapport de préflight, les 103 validations
éditoriales et la chronologie COG sont vérifiés avant la génération.
Aucun mouvement communal ni contour historique n'est modifié ou inféré.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re

from preparer_validations_pactols_corse_2026 import FIELDS

SCHEMA="adlfi.lieux.pactols.paca.complement.2026.public.v1"
SOURCE_CSV="recette/lieux/PACA-CANDIDATS-EXACTMATCH-2026.csv"
SOURCE_RAPPORT="recette/lieux/PACA-PREFLIGHT-EXACTMATCH-2026.json"
CSV_SHA="647ba3e1fdfd80199b854b512f12269379edaf910f47e34b7f53650ce2844925"
REPORT_SHA="a1d032da4c06a69c7d77ec8b6d28977856cc1e22bec1260d5d8e8550303c5a22"
SOURCE_RDF_SHA="3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7"
DATE_VALIDATION="2026-11-18"
DEPARTMENTS={"04","05","06","13","83","84"}
ARK=re.compile(r"^26678/[A-Za-z0-9]+$")

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as fd:
        for block in iter(lambda:fd.read(1048576),b""):
            h.update(block)
    return h.hexdigest()

def current_codes(cog):
    if (cog.get("region")!="paca" or cog.get("millesime_cog")!=2026
        or cog.get("geometries_historiques")!=[]):
        raise ValueError("COG PACA historique inattendu")
    current={}
    for row in cog["periodes_com"]:
        if (row["typecom"]=="COM" and row["debut_inclus"]<="2026-01-01"
            and (row["fin_exclue"] is None or row["fin_exclue"]>"2026-01-01")):
            code=row["code_insee"]
            if code in current:
                raise ValueError("Code courant PACA en doublon : "+code)
            current[code]=row["libelle"]
    if len(current)!=946:
        raise ValueError("946 communes COG PACA attendues")
    return current

def construire(registre:list[dict],rapport:dict,pilote:dict,cog:dict)->dict:
    if rapport.get("schema")!="adlfi.lieux.paca.exactmatch.preflight.2026.v1":
        raise ValueError("Rapport de préflight PACA inconnu")
    b=rapport["bilan"]
    if any(b[k]!=v for k,v in {
        "communes_COG_PACA_2026":946,"pilotage_editeur_conserve":103,
        "pilote_devoluy_multiple_ARK":1,
        "candidats_eligibles_avant_preflight":832,
        "candidats_conformes_apres_preflight":832,
        "candidats_mis_en_quarantaine_URI":0,
        "exceptions_paca_hors_pilote":11,
        "nouvelles_relations_publiees":0,
        "geometries_modifiees":0,"relations_historiques_inferees":0,
    }.items()):
        raise ValueError("Effectifs du préflight PACA divergents")
    if rapport.get("quarantaines_URI_INSEE") or len(rapport.get("exceptions_cog_pactols",[]))!=11:
        raise ValueError("Quarantaines ou exceptions modifiées")
    if rapport.get("source_RDF_sha256")!=SOURCE_RDF_SHA or rapport.get("date_COG")!="2026-01-01":
        raise ValueError("RDF ou COG du préflight différents")
    current=current_codes(cog)
    pilot_links=pilote.get("autorites",[])
    if (pilote.get("totaux",{}).get("autorites_pactols")!=103
        or len(pilot_links)!=103 or len(rapport["pilotage_valide_2026"])!=103):
        raise ValueError("Pilote 103 PACA altéré")
    pilot={}
    pilot_arks=set()
    for a in pilot_links:
        if len(a.get("correspondances",[]))!=1:
            raise ValueError("Pilote non univoque")
        link=a["correspondances"][0]
        code=link["code_insee"]
        if (code not in current or code in pilot
            or link["millesime_cog"]!=2026 or link["libelle_cog"]!=current[code]
            or link["relation_editoriale"]!="correspondance_communale_validee"
            or link["validation"]["statut"]!="VALIDE_EDITEUR_2026_10_18"
            or not ARK.fullmatch(a["ark_pactols"])):
            raise ValueError("Correspondance antérieure invalidée : "+code)
        pilot[code]=a["ark_pactols"]
        pilot_arks.add(a["ark_pactols"])
    if len(pilot_arks)!=103:
        raise ValueError("ARK du pilote non uniques")
    if {x["code_insee"]:x["ark_pactols"] for x in rapport["pilotage_valide_2026"]}!=pilot:
        raise ValueError("Rapport de préflight différent du pilote")
    exceptions={x["code_insee"] for x in rapport["exceptions_cog_pactols"]}
    if exceptions & set(pilot) or len(exceptions)!=11 or "05139" in exceptions:
        raise ValueError("Exceptions PACA invalides")
    if pilot.get("05139")!="26678/pcrtSeD2WMEIYA":
        raise ValueError("Validation éditoriale Dévoluy absente")
    if len(registre)!=832:
        raise ValueError("832 décisions supplémentaires attendues")
    links=[]
    seenCodes=set()
    seenArks=set()
    for row in registre:
        code=row["code_insee"]
        ark=row["ark_pactols"]
        if (len(code)!=5 or code[:2] not in DEPARTMENTS and code[:2]!="13"
            or code not in current or code in seenCodes or code in pilot or code in exceptions
            or not ARK.fullmatch(ark) or ark in seenArks or ark in pilot_arks
            or row["libelle_COG_2026"]!=current[code]
            or row["region_COG_2026"]!="93"
            or row["departement_COG_2026"] not in DEPARTMENTS
            or not code.startswith(row["departement_COG_2026"])
            or row["uri_insee"]!="http://id.insee.fr/geo/commune/"+code
            or row["source_rdf_sha256"]!=SOURCE_RDF_SHA
            or row["predicat_source"]!="skos:exactMatch"
            or row["statut_validation"]!="CANDIDAT_CONFORME_EXACTMATCH_UNIVOQUE_PRE_PUBLICATION"
            or row["portee_COG"]!="2026-01-01"
            or row["type_decision"]!="REGLE_EXACTMATCH_UNIVOQUE_AVEC_CONTROLE_URIS"
            or row["publication_site"]!="EN_ATTENTE_RECETTE_PUBLICATION"
            or not row["prefLabel_fr_pactols"]):
            raise ValueError("Ligne de registre non admissible : "+code)
        seenCodes.add(code)
        seenArks.add(ark)
        links.append({
            "code_insee":code,"libelle_COG_2026":row["libelle_COG_2026"],
            "ark_pactols":ark,"libelle_pactols":row["prefLabel_fr_pactols"],
            "uri_insee":row["uri_insee"],"predicat_source":"skos:exactMatch",
            "millesime_validation":2026,"date_validation":DATE_VALIDATION,
            "statut":"correspondance_PACA_validee_par_regle_2026",
            "type_validation":"exactMatch_univoque_avec_preflight_URIs_INSEE",
        })
    if len(seenCodes)!=832 or seenCodes&set(pilot) or seenCodes&exceptions:
        raise ValueError("Codes PACA en collision")
    if set(current)!=seenCodes|set(pilot)|exceptions:
        raise ValueError("Répartition exhaustive des 946 communes PACA incohérente")
    return {
        "schema":SCHEMA,"region":"paca","millesime_cog":"2026-01-01",
        "source_rdf":"Pactols_Lieux_th17_20260722.rdf",
        "source_rdf_sha256":SOURCE_RDF_SHA,
        "source_registre":SOURCE_CSV,"sha256_registre":CSV_SHA,
        "source_preflight":SOURCE_RAPPORT,"sha256_preflight":REPORT_SHA,
        "nombre_ajouts":832,"pilote_valide_conserve":103,
        "nombre_total_alignements_2026":935,"communes_a_instruire":11,
        "nouvelles_geometries":0,"liens_historiques_inferes":0,
        "alignements_Pactols_COG_valides_2026":sorted(links,key=lambda x:x["code_insee"]),
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ("registre","preflight","pilote","cog","sortie"):
        p.add_argument("--"+arg,required=True,type=Path)
    a=p.parse_args()
    if a.sortie.exists() or a.sortie.resolve() in [x.resolve() for x in (a.registre,a.preflight,a.pilote,a.cog)]:
        raise ValueError("Sortie doit être nouvelle et distincte")
    if digest(a.registre)!=CSV_SHA or digest(a.preflight)!=REPORT_SHA:
        raise ValueError("Empreinte de registre ou de préflight différente")
    with a.registre.open(encoding="utf-8",newline="") as fd:
        reader=csv.DictReader(fd,delimiter=";")
        if tuple(reader.fieldnames or ())!=FIELDS:
            raise ValueError("Colonnes du registre PACA incompatibles")
        rows=list(reader)
    report=json.loads(a.preflight.read_text(encoding="utf-8"))
    pilote=json.loads(a.pilote.read_text(encoding="utf-8"))
    cog=json.loads(a.cog.read_text(encoding="utf-8"))
    result=construire(rows,report,pilote,cog)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(result,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    print("PACA_832_PUBLICATION_PREPAREE",json.dumps({
        "ajouts":832,"pilote_conserve":103,"ensemble":935,
        "exceptions":11,"sha256_json":digest(a.sortie),
        "nouvelles_geometries":0
    },ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
