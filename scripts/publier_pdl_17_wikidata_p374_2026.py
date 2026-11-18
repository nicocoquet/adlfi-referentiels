#!/usr/bin/env python3
"""Publier 17 liens PDL par la chaîne Pactols exactMatch Wikidata P374 → COG 2026.

Cette publication ne crée pas et ne revendique pas d'exactMatch Pactols direct
vers id.insee.fr. Les identités des communes anciennes restent indépendantes.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from auditer_pactols_cog_regions_prioritaires_2026 import sha
from auditer_pactols_polynesie_2026 import RDF_SHA,norm
from prequalifier_pdl_17_sans_insee_2026 import analyser_concepts

SCHEMA="adlfi.lieux.pactols.pdl.wikidata-p374.2026.public.v1"
QUALIF_SCHEMA="adlfi.lieux.pdl.17-wikidata-p374.2026.registre-non-validant.v1"
ORIG_SCHEMA="adlfi.lieux.pdl.24-divergences.2026.registre-non-validant.v1"
SOURCE="recette/lieux/PDL-17-WIKIDATA-P374-PUBLICATION-2026.md"
QUALIF_SOURCE="recette/lieux/PDL-17-WIKIDATA-P374-2026.json"
INSEE_ROOT="http://id.insee.fr/geo/commune/"

def publier(rdf:Path,cog:dict,qualif:dict,origin:dict,publications:list[dict])->dict:
    if sha(rdf)!=RDF_SHA:
        raise ValueError("Le snapshot Pactols ne correspond pas au SHA-256 épinglé")
    if cog.get("region")!="pdl" or cog.get("millesime_cog")!=2026:
        raise ValueError("COG historique PDL 2026 requis")
    if (qualif.get("schema")!=QUALIF_SCHEMA or
        qualif.get("nombre_dossiers")!=17 or
        qualif.get("identifiants_P374_concordants")!=17 or
        qualif.get("nouveaux_alignements")!=0 or
        origin.get("schema")!=ORIG_SCHEMA or origin.get("nombre_dossiers")!=24):
        raise ValueError("Registres de preuve incomplets")
    existing=[a for d in publications for a in d["alignements_Pactols_COG_valides_2026"]]
    used_codes={a["code_insee"] for a in existing}
    used_arks={a["ark_pactols"] for a in existing}
    if len(existing)!=1195 or len(used_codes)!=1195 or len(used_arks)!=1195:
        raise ValueError("Publication existante 1195 incohérente")
    origin_bycode={x["code_insee"]:x for x in origin["dossiers"]}
    evidence=qualif["dossiers"]
    if len(evidence)!=17 or len({x["code_insee_2026"] for x in evidence})!=17 or len({x["qid_wikidata"] for x in evidence})!=17:
        raise ValueError("Les preuves doivent décrire 17 communes et 17 QID distincts")
    targets={x["code_insee_2026"]:x["libelle_COG_2026"] for x in evidence}
    concepts,homonymes=analyser_concepts(rdf,targets)
    all_current=[x for x in cog["periodes_com"] if
                 x["typecom"]=="COM" and x["debut_inclus"]<="2026-01-01" and
                 (x["fin_exclue"] is None or x["fin_exclue"]>"2026-01-01")]
    if len(all_current)!=1228 or len({x["code_insee"] for x in all_current})!=1228:
        raise ValueError("Le COG actuel PDL doit porter 1228 communes uniques")
    actual={x["code_insee"]:x for x in all_current}
    result=[]
    for x in sorted(evidence,key=lambda z:z["code_insee_2026"]):
        code=x["code_insee_2026"]
        old=origin_bycode.get(code)
        if not old or old["candidat_actuel"] is None:
            raise ValueError("Absence du concept actuel dans le registre 24 : "+code)
        ark=old["candidat_actuel"]["ark"]
        qid=x["qid_wikidata"]
        uriwiki="https://www.wikidata.org/wiki/"+qid
        if (old["candidat_actuel"]["situation_URI_INSEE"]!="AUCUN_EXACTMATCH_INSEE" or
            code in used_codes or ark in used_arks or
            old["ark_concept_historique"]==ark or
            old["ark_concept_historique"] in used_arks or
            x["statut_prequalification"]!="P374_CONCORDE_COG_2026" or
            x["insee_P374_actif_2026"]!=[code] or
            x["P31_instances"]!=["Q484170"] or
            x["P571_creation"]!=[x["date_creation_COG_2026"]] or
            x["decision_editoriale"]!="NON_PRISE" or
            x["publication"]!="NON_PUBLIE" or
            not isinstance(x["revision_wikidata"],int) or x["revision_wikidata"]<=0 or
            x["revision_url"]!=
                "https://www.wikidata.org/w/index.php?title="+qid+"&oldid="+str(x["revision_wikidata"])):
            raise ValueError("La qualification Wikidata n'est pas admissible : "+code)
        p=concepts.get(ark)
        if (not p or p["deprecated"] or p["isReplacedBy"] or
            p["exactMatch"]!=[uriwiki] or
            homonymes.get(code)!=[ark] or
            len(p["prefLabels_fr"])!=1 or
            norm(p["prefLabels_fr"][0])!=norm(x["libelle_COG_2026"])):
            raise ValueError("Le concept RDF est contradictoire ou homonyme : "+code)
        cur=actual.get(code)
        if (not cur or cur["libelle"]!=x["libelle_COG_2026"] or
            cur["debut_inclus"]!=x["date_creation_COG_2026"]):
            raise ValueError("Identité 2026 non attestée au COG : "+code)
        moves=[m for m in cog["lignes_mouvements_cog"] if
               m["date_effet"]==cur["debut_inclus"] and m["mod"]=="32" and
               m["code_apres"]==code and m["typecom_apres"]=="COM" and
               m["libelle_apres"]==cur["libelle"]]
        if not moves:
            raise ValueError("Création de commune nouvelle MOD32 absente : "+code)
        earlier=[c for c in cog["periodes_com"] if
                 c["code_insee"]==code and c["typecom"]=="COM" and
                 c["fin_exclue"]==cur["debut_inclus"] and
                 norm(c["libelle"])==norm(old["prefLabel_historique"].split(" (")[0])]
        if len(earlier)!=1:
            raise ValueError("Ancien épisode communal non attesté : "+code)
        result.append({
           "code_insee":code,
           "libelle_COG_2026":cur["libelle"],
           "libelle_pactols":p["prefLabels_fr"][0],
           "ark_pactols":ark,
           "ark_ancienne_commune_distinct":old["ark_concept_historique"],
           "libelle_ancienne_commune":old["prefLabel_historique"],
           "URI_Wikidata_exactMatch":uriwiki,
           "qid_Wikidata":qid,
           "revision_Wikidata":x["revision_wikidata"],
           "revision_Wikidata_url":x["revision_url"],
           "code_INSEE_Wikidata_P374":code,
           "predicat_Pactols":"skos:exactMatch",
           "predicat_Wikidata_INSEE":"P374",
           "source_RDF_Pactols_sha256":RDF_SHA,
           "source_qualification":QUALIF_SOURCE,
           "source_registre":SOURCE,
           "date_creation_COG":cur["debut_inclus"],
           "nature_evenement_COG":"MOD32_CREATION_COMMUNE_NOUVELLE",
           "date_validation":"2026-11-18",
           "millesime_validation":2026,
           "statut":"correspondance_PDL_Wikidata_P374_validee_2026",
           "portee_chronologique":"2026_SEULEMENT",
           "relations_historiques_inferees":0,
        })
    if len(result)!=17 or len({r["ark_pactols"] for r in result})!=17:
        raise ValueError("Le lot 17 doit être constitué de concepts uniques")
    return {
        "schema":SCHEMA,"region":"pdl","millesime_cog":"2026-01-01",
        "source_RDF_Pactols_sha256":RDF_SHA,"source_registre":SOURCE,
        "source_qualification":QUALIF_SOURCE,
        "source_COG":"docs/data/lieux-chronologie/cog-pdl.json",
        "alignements_publies_precedemment":1195,"nouveaux_alignements":17,
        "total_alignements_PDL_2026":1212,"communes_PDL_COG_2026":1228,
        "communes_a_instruire":16,"geometries_nouvelles":0,
        "liens_historiques_inferes":0,
        "alignements_Pactols_COG_valides_2026":result
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("rdf","cog","qualif","origine","base","uuid","lot01",
                 "chemille","lot02","oree","sortie"):
        p.add_argument("--"+name,type=Path,required=True)
    args=p.parse_args()
    if args.sortie.exists():raise ValueError("Refus d'écraser le fichier généré")
    load=lambda path:json.loads(path.read_text(encoding="utf-8"))
    publication=publier(args.rdf,load(args.cog),load(args.qualif),load(args.origine),
                       [load(args.base),load(args.uuid),load(args.lot01),
                        load(args.chemille),load(args.lot02),load(args.oree)])
    args.sortie.parent.mkdir(parents=True,exist_ok=True)
    args.sortie.write_text(json.dumps(publication,ensure_ascii=False,
                                     sort_keys=True,separators=(",",":"))+"\n",
                           encoding="utf-8")
    print("PDL_17_WIKIDATA_PUBLICATION",json.dumps({
        "ajoutes":17,"total":1212,"exceptions":16,
        "geometries":0,"successions":0},sort_keys=True))
if __name__=="__main__":
    main()
