#!/usr/bin/env python3
"""Bilan de couverture Pactols–COG des communes ultramarines publiées (2026).

Ce script vérifie le référentiel publié et les registres de décisions
éditoriales en place. Il n'infère JAMAIS une nouvelle association, même en cas
d'homonymie, de code présent, ou d'URI signalée sans décision.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

COUNTS={"971":32,"972":34,"973":22,"974":24,"975":2,"976":17,"987":48,"988":33}
REGISTRES={
    "971":"GUADELOUPE",
    "972":"MARTINIQUE",
    "973":"GUYANE",
    "974":"REUNION",
    "987":"POLYNESIE",
}
COLLECTIVITES={"977","978","986","987"}
STATUS="VALIDE_ADLFI_2026"
DATE="2026-01-01"

def lire_registre(path:Path):
    with path.open(encoding="utf-8-sig",newline="") as stream:
        reader=csv.DictReader(stream,delimiter=";")
        fields={"code_insee","libelle_COG_2026","ark_pactols","uri_insee",
                "predicat_source","concept_deprecie","statut_validation",
                "portee_COG","prefLabel_fr_pactols"}
        if set(reader.fieldnames or [])!=fields:
            raise ValueError("Schéma de registre inattendu : "+path.name)
        return list(reader)

def audit(index_path:Path,registres_dir:Path):
    data=json.loads(index_path.read_text(encoding="utf-8"))
    if data.get("schema")!="adlfi.lieux.recherche.outremer.public.v1":
        raise ValueError("Schéma de publication incompatible")
    communes=data["communes"]
    if set(communes)!=set(COUNTS):
        raise ValueError("Territoires communaux publiés inattendus")
    current={}
    zones={}
    for prefix,expected in COUNTS.items():
        raw=communes[prefix].splitlines()
        rows=[l.split("|",1) for l in raw]
        if len(rows)!=expected or any(len(r)!=2 or not r[0].startswith(prefix) for r in rows):
            raise ValueError("Liste communale COG incohérente : "+prefix)
        if len({r[0] for r in rows})!=expected:
            raise ValueError("Code COG dupliqué : "+prefix)
        zones[prefix]={r[0]:r[1] for r in rows}
        if any(c in current for c in zones[prefix]):
            raise ValueError("Code COG présent dans deux zones")
        current.update(zones[prefix])
    valid=data["pactols_valides"]
    if not isinstance(valid,dict) or any(c not in current for c in valid):
        raise ValueError("Alignement publié sans commune de référence")
    if len(set(valid.values()))!=len(valid):
        raise ValueError("ARK dupliqué dans les alignements")
    if len(valid)!=212:
        raise ValueError("Effectif publié attendu 212, trouvé "+str(len(valid)))
    confirmed=data.get("ark_confirmes_non_valides",{})
    if confirmed!={}:
        raise ValueError("L’ARK confirmé de Dembeni doit être promu après preuve RDF")
    if any(c in valid for c in confirmed):
        raise ValueError("ARK confirmé à tort considéré validé")
    if set(confirmed.values()) & set(valid.values()):
        raise ValueError("ARK confirmé et validé simultanément")
    collectives=data.get("pactols_collectivites_valides",{})
    if set(collectives)!=COLLECTIVITES or len(set(collectives.values()))!=4:
        raise ValueError("Les 4 collectivités validées ont changé")
    if set(collectives.values()) & (set(valid.values())|set(confirmed.values())):
        raise ValueError("Une collectivité est confondue avec une commune")

    registry_codes=set()
    rapport=[]
    for prefix,expected in COUNTS.items():
        approved={k:v for k,v in valid.items() if k.startswith(prefix)}
        row={"territoire":prefix,"communes_COG_2026":expected,
             "alignements_pactols_valides":len(approved),
             "sans_alignement_valide":expected-len(approved),
             "codes_sans_alignement":sorted(set(zones[prefix])-set(approved)),
             "registres_verifies":False}
        if prefix in REGISTRES:
            file=registres_dir/(REGISTRES[prefix]+"-VALIDATIONS-PACTOLS-COG-2026.csv")
            rows=lire_registre(file)
            if len(rows)!=expected:
                raise ValueError("Nombre de décisions inattendu : "+file.name)
            seen=set()
            for r in rows:
                code=r["code_insee"]
                if code in seen or code in registry_codes:
                    raise ValueError("Décision dupliquée : "+code)
                seen.add(code)
                registry_codes.add(code)
                uri="http://id.insee.fr/geo/commune/"+code
                if (code not in zones[prefix] or
                    zones[prefix][code]!=r["libelle_COG_2026"] or
                    valid.get(code)!=r["ark_pactols"] or
                    r["uri_insee"]!=uri or
                    r["predicat_source"] not in ("exactMatch","skos:exactMatch") or
                    r["concept_deprecie"]!="non" or
                    r["statut_validation"]!=STATUS or
                    r["portee_COG"]!=DATE):
                    raise ValueError("Registre non concordant avec la publication : "+code)
            if seen!=set(zones[prefix]):
                raise ValueError("Registre incomplet : "+prefix)
            row["registres_verifies"]=True
            row["registre"]=file.name
        rapport.append(row)
    # Les 36 décisions supplémentaires disposent d'un registre spécialisé.
    additions=registres_dir/"VALIDATIONS-NC-SPM-DEMBENI-2026.csv"
    with additions.open(encoding="utf-8-sig",newline="") as stream:
        reader=csv.DictReader(stream,delimiter=";")
        required={"code_insee","libelle_COG_2026","ark_pactols","uri_insee",
                  "predicat_source","source","statut_validation","portee_COG",
                  "qualification","note_editoriale"}
        if set(reader.fieldnames or ())!=required:
            raise ValueError("Schéma du registre de 36 décisions différent")
        new=list(reader)
    if len(new)!=36 or len(registry_codes)!=160:
        raise ValueError("160 décisions anciennes et 36 nouvelles attendues")
    newly_seen=set()
    for r in new:
        code=r["code_insee"]
        if (code not in current or code in registry_codes or code in newly_seen
            or r["libelle_COG_2026"]!=current[code]
            or r["uri_insee"]!="http://id.insee.fr/geo/commune/"+code
            or r["predicat_source"]!="skos:exactMatch"
            or r["statut_validation"]!="VALIDE_ADLFI_2026"
            or r["portee_COG"]!=DATE or valid.get(code)!=r["ark_pactols"]):
            raise ValueError("Nouvelle décision non concordante : "+code)
        newly_seen.add(code)
    if len(newly_seen & {c for c in valid if c.startswith("988")})!=33:
        raise ValueError("Les 33 correspondances de Nouvelle-Calédonie manquent")
    registry_codes.update(newly_seen)
    if len(registry_codes)!=196 or set(valid)-registry_codes!=set(
       c for c in valid if c.startswith("976") and c!="97607"):
        raise ValueError("Registres insuffisants pour expliquer les 212 liens")
    mayo={c for c in valid if c.startswith("976")}
    if len(mayo)!=17 or valid.get("97607")!="26678/crtZcuFSJVYZU":
        raise ValueError("Mayotte : validation Dembeni absente")
    return {
        "schema":"adlfi.lieux.couverture.pactols.cog.outremer.2026.audit.v1",
        "statut":"INVENTAIRE_NON_VALIDANT",
        "publication_suivie":"docs/data/lieux-outremer/recherche-2026.json",
        "index_sha256":hashlib.sha256(index_path.read_bytes()).hexdigest(),
        "millesime":DATE,
        "totaux":{"communes":sum(COUNTS.values()),
                  "alignements_communaux":len(valid),
                  "sans_alignement_communal":sum(COUNTS.values())-len(valid),
                  "validations_registres_verifiees":len(registry_codes),
                  "autres_validations_mayotte":len(mayo),
                  "collectivites_distinctes":len(collectives)},
        "territoires":rapport,
        "ark_confirmes_non_valides":confirmed,
        "priorites":[
          {"cible":"ALIGNEMENTS_METROPOLE_ET_COMMUNES_HISTORIQUES",
           "statut":"A_INSTRUIRE_HORS_COG_OUTREMER_2026"}
        ],
        "limites":[
           "Absence de lien validé ne signifie pas absence de concept Pactols",
           "Cinq registres territoriaux + 36 nouvelles décisions ; Mayotte initiale contrôlée par index public",
           "Décisions limitées aux identifiants du COG au 1er janvier 2026",
           "Les catégories administratives COMER, CIR et communes associées ne sont pas interchangeables",
           "Aucune inférence d'alignement sur la base du seul nom, code, contour ou succession",
        ],
        "publication":{"nouveaux_ark":0,"nouveaux_contours":0,"nouveaux_alignements":0},
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--index",required=True,type=Path)
    p.add_argument("--registres",required=True,type=Path)
    p.add_argument("--sortie",required=True,type=Path)
    a=p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Le rapport doit être écrit hors docs et sans écrasement")
    record=audit(a.index,a.registres)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(record,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("COUVERTURE_PACTOLS_COG",json.dumps({
        "totaux":record["totaux"],
        "territoires":[{k:r[k] for k in ("territoire","communes_COG_2026",
                    "alignements_pactols_valides","sans_alignement_valide")}
                      for r in record["territoires"]]
    },sort_keys=True,ensure_ascii=False))

if __name__=="__main__":main()
