#!/usr/bin/env python3
"""Publie cinq ARK PDL au COG 2026, sans les confondre avec les anciennes COM/COMD."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
from auditer_pactols_cog_regions_prioritaires_2026 import audit
from qualifier_pdl_ark_multiples_2026 import completer_rdf
from auditer_pactols_polynesie_2026 import RDF_SHA

SCHEMA="adlfi.lieux.pactols.pdl.lot01-communes-nouvelles.2026.public.v1"
SOURCE="recette/lieux/PDL-LOT01-CINQ-ARK-2026.csv"
CODES={"44005","44021","44029","44087","44163"}
URI="http://id.insee.fr/geo/commune/"

def publier(propositions:list[dict], cdata:dict, previous:dict, uuid:dict,
            resultat_audit:dict, supplements:dict) -> dict:
    if (cdata.get("region")!="pdl" or cdata.get("millesime_cog")!=2026 or
        previous.get("nombre_communes")!=1140 or
        len(previous.get("alignements_Pactols_COG_valides_2026",[]))!=1140 or
        uuid.get("total_alignements_PDL_2026")!=1143 or
        uuid.get("communes_a_instruire")!=85 or
        len(uuid.get("alignements_Pactols_COG_valides_2026",[]))!=3 or
        resultat_audit.get("pactols",{}).get("sha256")!=RDF_SHA):
        raise ValueError("Sources PDL préexistantes inattendues")
    rows={r["code_COG_2026"]:r for r in propositions}
    if len(rows)!=5 or set(rows)!=CODES:
        raise ValueError("Le registre doit contenir cinq codes distincts")
    already=previous["alignements_Pactols_COG_valides_2026"]+uuid["alignements_Pactols_COG_valides_2026"]
    usedcodes={a["code_insee"] for a in already}
    usedarks={a["ark_pactols"] for a in already}
    if len(usedcodes)!=1143 or len(usedarks)!=1143 or CODES&usedcodes:
        raise ValueError("Collision avec les 1143 validations")
    current={}
    for p in cdata["periodes_com"]:
        if (p["typecom"]=="COM" and p["debut_inclus"]<="2026-01-01" and
            (not p["fin_exclue"] or p["fin_exclue"]>"2026-01-01")):
            if p["code_insee"] in current:
                raise ValueError("Code COG 2026 répété")
            current[p["code_insee"]]=p["libelle"]
    if len(current)!=1228:
        raise ValueError("Effectif COG PDL 2026 inattendu")
    collisions={r["code"]:r for r in resultat_audit["communes"]
                if r["region"]=="52" and r["code"] in CODES}
    if set(collisions)!=CODES:
        raise ValueError("Cinq dossiers RDF absents")
    entries=[]
    for code in sorted(CODES):
        r=rows[code]
        name=r["nom_COG_2026"]
        ark=r["ark_candidat_actuel"]
        old=r["ark_concept_ancien"]
        past=r["libelle_concept_ancien"]
        date=r["date_MOD32"]
        if (r["statut"]!="PROPOSITION_A_CONTROLER" or r["portee"]!="2026-01-01" or
            date!="2016-01-01" or current[code]!=name or ark==old or
            ark in usedarks or old in usedarks or
            not ark.startswith("26678/") or not old.startswith("26678/")):
            raise ValueError("Proposition ou identité actuelle non conforme : "+code)
        hits=collisions[code]["preuves_RDF_exactMatch"]
        if len(hits)!=2 or {x["ark"] for x in hits}!={ark,old}:
            raise ValueError("ARK concurrents inattendus : "+code)
        for p, expected in ((next(x for x in hits if x["ark"]==ark),name),
                            (next(x for x in hits if x["ark"]==old),past)):
            if (p["prefLabels_fr"]!=[expected] or p["deprecie"] or p["remplace"] or
                p["insee_exactMatch"]!=[{"code":code,"famille":"commune","uri":URI+code}] or
                sorted(u for u in supplements[p["ark"]]["exactMatch_tous"]
                       if u.startswith(("http://id.insee.fr/geo/",
                                        "https://id.insee.fr/geo/"))) != [URI+code]):
                raise ValueError("Preuve Pactols ambiguë : "+p["ark"]+" "+repr({"prefLabels":p["prefLabels_fr"],"insee":p["insee_exactMatch"],"status":(p["deprecie"],p["remplace"]),"exact_INSEE":sorted(u for u in supplements[p["ark"]]["exactMatch_tous"] if "id.insee.fr/geo/" in u)}))
        moves=cdata["lignes_mouvements_cog"]
        if (not any(m["date_effet"]==date and m["mod"]=="32" and
                    m["code_apres"]==code and m["libelle_apres"]==name and
                    m["typecom_apres"]=="COM" for m in moves) or
            not any(m["date_effet"]==date and m["mod"]=="32" and
                    m["code_avant"]==code and m["code_apres"]==code and
                    m["libelle_apres"]==past and m["typecom_apres"]=="COMD"
                    for m in moves)):
            raise ValueError("Deux états COG historiques non confirmés : "+code)
        entries.append({
            "ark_pactols":ark,"ark_ancienne_commune_distinct":old,
            "code_insee":code,"libelle_COG_2026":name,"libelle_pactols":name,
            "libelle_ancienne_commune":past,
            "uri_insee":URI+code,"predicat_source":"skos:exactMatch",
            "source_RDF_Pactols_sha256":RDF_SHA,
            "source_registre":SOURCE,"date_evenement_COG":date,
            "nature_evenement_COG":"MOD32_CREATION_COMMUNE_NOUVELLE",
            "type_ancienne_commune_apres":"COMD",
            "date_validation":"2026-11-18","millesime_validation":2026,
            "statut":"correspondance_PDL_commune_nouvelle_validee_2026",
            "portee_chronologique":"2026_SEULEMENT","relations_historiques_inferees":0
        })
    if len({x["ark_pactols"] for x in entries})!=5 or len({x["ark_ancienne_commune_distinct"] for x in entries})!=5:
        raise ValueError("ARK dupliqués")
    return {"schema":SCHEMA,"region":"pdl","millesime_cog":"2026-01-01",
            "source_registre":SOURCE,"source_RDF_Pactols_sha256":RDF_SHA,
            "alignements_publies_precedemment":1143,
            "nouveaux_alignements":5,
            "total_alignements_PDL_2026":1148,
            "communes_PDL_COG_2026":1228,"communes_a_instruire":80,
            "nouvelles_geometries":0,"liens_historiques_inferes":0,
            "alignements_Pactols_COG_valides_2026":entries}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for field in ("registre","cog","precedent","uuid","rdf","cog-officiel","sortie"):
        parser.add_argument("--"+field,required=True,type=Path)
    a=parser.parse_args()
    if a.sortie.exists():
        raise ValueError("Ne pas écraser un résultat")
    with a.registre.open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f,delimiter=";"))
    load=lambda p: json.loads(p.read_text(encoding="utf-8"))
    rd=audit(a.rdf,a.cog_officiel) # empreintes RDF et COG officielles contrôlées
    arks={x[k] for x in rows for k in ("ark_candidat_actuel","ark_concept_ancien")}
    extra=completer_rdf(a.rdf,arks)
    d=publier(rows,load(a.cog),load(a.precedent),load(a.uuid),rd,extra)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(d,ensure_ascii=False,sort_keys=True,
                                   separators=(",",":"))+"\n",encoding="utf-8")
    print("PDL_1148_LOT01",json.dumps({"ajoutes":5,"total":1148,"exceptions":80,
        "anciens_ARK_promus":0,"geometries":0},sort_keys=True))
if __name__=="__main__":
    main()
