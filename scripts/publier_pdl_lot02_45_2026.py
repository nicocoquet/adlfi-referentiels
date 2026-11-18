#!/usr/bin/env python3
"""Publier les 45 identités PDL triées par preuve RDF/COG, sans rétroprojection."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from prequalifier_pdl_lot02_2026 import preparer
from auditer_pactols_polynesie_2026 import RDF_SHA

SCHEMA="adlfi.lieux.pactols.pdl.lot02.2026.public.v1"
SOURCE="recette/lieux/PDL-LOT02-45-COMMUNES-NOUVELLES-2026.md"
URI="http://id.insee.fr/geo/commune/"

def publier(rdf:Path,cog_source:Path,chronologie:dict,
            publications:list[dict])->dict:
    recette=preparer(rdf,cog_source,chronologie,publications)
    if (recette["restants"]!=54 or
        recette["groupes"]!={"CANDIDAT_LOT02_A_VERIFIER":45,
                           "INSTRUCTION_COMPLEMENTAIRE":9} or
        recette["liens_publies_avant_recette"]!=1149 or
        recette["nouveaux_alignements"]!=0 or
        recette["source_RDF_Pactols_sha256"]!=RDF_SHA):
        raise ValueError("Recette des 54 collisions inattendue")
    previous=[a for r in publications for a in r["alignements_Pactols_COG_valides_2026"]]
    usedcodes={a["code_insee"] for a in previous}
    usedarks={a["ark_pactols"] for a in previous}
    if len(previous)!=len(usedcodes)!=len(usedarks):
        raise ValueError("Publications précédentes comportant des doublons")
    if len(previous)!=1149:
        raise ValueError("1149 alignements antérieurs requis")
    current={p["code_insee"]:p for p in chronologie["periodes_com"]
             if p["typecom"]=="COM" and p["debut_inclus"]<="2026-01-01" and
             (p["fin_exclue"] is None or p["fin_exclue"]>"2026-01-01")}
    if len(current)!=1228:
        raise ValueError("1228 communes COG PDL 2026 requises")
    entries=[]
    for r in recette["dossiers"]:
        if r["statut_prequalification"]!="CANDIDAT_LOT02_A_VERIFIER":
            continue
        code=r["code_COG_2026"]
        ark=r["ark_candidat_2026"]
        ancien=r["ark_historique_distinct"]
        name=r["nom_COG_2026"]
        prevname=r["libelle_historique"]
        date=r["date_creation_MOD32"]
        if (r["motifs_controle"] or not ark or not ancien or
            not prevname or not date or ark==ancien or
            ark in usedarks or ancien in usedarks or
            code in usedcodes or current[code]["libelle"]!=name or
            current[code]["debut_inclus"]!=date or
            not ark.startswith("26678/") or not ancien.startswith("26678/")):
            raise ValueError("Dossier non admissible à publication : "+code)
        rows=[m for m in chronologie["lignes_mouvements_cog"]
              if m["mod"]=="32" and m["date_effet"]==date and
              m["code_apres"]==code]
        if (not any(m["typecom_apres"]=="COM" and m["libelle_apres"]==name
                    for m in rows) or
            not any(m["code_avant"]==code and
                    m["typecom_avant"]=="COM" and m["typecom_apres"]=="COMD" and
                    m["libelle_apres"]==prevname for m in rows)):
            raise ValueError("Épisodes MOD32 non établis : "+code)
        entries.append({
          "code_insee":code,"libelle_COG_2026":name,
          "libelle_pactols":name,"ark_pactols":ark,
          "ark_ancienne_commune_distinct":ancien,
          "libelle_ancienne_commune":prevname,
          "uri_insee":URI+code,"predicat_source":"skos:exactMatch",
          "source_RDF_Pactols_sha256":RDF_SHA,
          "source_registre":SOURCE,"date_evenement_COG":date,
          "nature_evenement_COG":"MOD32_CREATION_COMMUNE_NOUVELLE",
          "type_ancienne_commune_apres":"COMD",
          "millesime_validation":2026,"date_validation":"2026-11-18",
          "statut":"correspondance_PDL_commune_nouvelle_validee_2026",
          "portee_chronologique":"2026_SEULEMENT",
          "relations_historiques_inferees":0
        })
    if len(entries)!=45 or len({r["code_insee"] for r in entries})!=45 or len({r["ark_pactols"] for r in entries})!=45 or len({r["ark_ancienne_commune_distinct"] for r in entries})!=45:
        raise ValueError("Les 45 candidats doivent être uniques")
    if ({r["ark_pactols"] for r in entries} &
        {r["ark_ancienne_commune_distinct"] for r in entries}):
        raise ValueError("ARK ancien utilisé comme ARK de commune nouvelle")
    return {
      "schema":SCHEMA,"region":"pdl","millesime_cog":"2026-01-01",
      "source_registre":SOURCE,
      "source_RDF_Pactols_sha256":RDF_SHA,
      "source_qualification":"recette/lieux/PDL-LOT02-PREQUALIFICATION-2026.md",
      "alignements_publies_precedemment":1149,
      "nouveaux_alignements":45,"total_alignements_PDL_2026":1194,
      "communes_PDL_COG_2026":1228,"communes_a_instruire":34,
      "codes_multiples_restant_a_instruire":9,
      "divergences_restantes":24,"cas_Rives_du_Fougerais_exclu":"85292",
      "nouvelles_geometries":0,"liens_historiques_inferes":0,
      "alignements_Pactols_COG_valides_2026":sorted(entries,key=lambda a:a["code_insee"])
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("rdf","cog-officiel","chronologie","base","uuid","lot01","chemille","sortie"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    if a.sortie.exists():
        raise ValueError("Fichier de sortie déjà existant")
    read=lambda path:json.loads(path.read_text(encoding="utf-8"))
    d=publier(a.rdf,a.cog_officiel,read(a.chronologie),
              [read(a.base),read(a.uuid),read(a.lot01),read(a.chemille)])
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(d,sort_keys=True,ensure_ascii=False,
                                   separators=(",",":"))+"\n",encoding="utf-8")
    print("PDL_LOT02_1194",json.dumps({"ajoutes":45,"total":1194,
          "exceptions":34,"anciens_promus":0,"geometries":0},sort_keys=True))
if __name__=="__main__":
    main()
