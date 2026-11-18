#!/usr/bin/env python3
"""Publier Chemillé-en-Anjou 2026 en distinguant les trois épisodes du code 49092."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from auditer_pactols_cog_regions_prioritaires_2026 import audit
from qualifier_pdl_ark_multiples_2026 import completer_rdf
from auditer_pactols_polynesie_2026 import RDF_SHA

SCHEMA="adlfi.lieux.pactols.pdl.chemille.2026.public.v1"
CODE="49092"
NOM="Chemillé-en-Anjou"
URI="http://id.insee.fr/geo/commune/"+CODE
ARKS={
 "Chemillé":"26678/pcrtL5GRFXn3Zs",
 "Chemillé-Melay":"26678/pcrtWU8rdgPSSH",
 "Chemillé-en-Anjou":"26678/pcrtzDf0WnnRyr"
}
SOURCE="recette/lieux/PDL-CHEMILLE-49092-2026.md"

def publier(cog:dict,base:dict,uuid:dict,lot01:dict,regional:dict,
            complement:dict)->dict:
    if (cog.get("region")!="pdl" or cog.get("millesime_cog")!=2026 or
        base.get("nombre_communes")!=1140 or
        len(base.get("alignements_Pactols_COG_valides_2026",[]))!=1140 or
        uuid.get("total_alignements_PDL_2026")!=1143 or
        len(uuid.get("alignements_Pactols_COG_valides_2026",[]))!=3 or
        lot01.get("total_alignements_PDL_2026")!=1148 or
        lot01.get("communes_a_instruire")!=80 or
        len(lot01.get("alignements_Pactols_COG_valides_2026",[]))!=5 or
        regional.get("pactols",{}).get("sha256")!=RDF_SHA):
        raise ValueError("Provenance ou publications PDL antérieures incohérentes")
    previous=(base["alignements_Pactols_COG_valides_2026"]+
              uuid["alignements_Pactols_COG_valides_2026"]+
              lot01["alignements_Pactols_COG_valides_2026"])
    used_codes={r["code_insee"] for r in previous}
    used_arks={r["ark_pactols"] for r in previous}
    if (len(previous)!=1148 or len(used_codes)!=1148 or len(used_arks)!=1148 or
        CODE in used_codes or set(ARKS.values())&used_arks):
        raise ValueError("Collision avec les 1148 validations précédentes")
    current=[r for r in cog["periodes_com"] if
             r["typecom"]=="COM" and r["debut_inclus"]<="2026-01-01" and
             (r["fin_exclue"] is None or r["fin_exclue"]>"2026-01-01")]
    if len(current)!=1228 or len({r["code_insee"] for r in current})!=1228:
        raise ValueError("COG PDL 2026 incomplet")
    if [r["libelle"] for r in current if r["code_insee"]==CODE]!=[NOM]:
        raise ValueError("Identité actuelle Chemillé absente du COG")
    episodes=sorted((r for r in cog["periodes_com"]
                     if r["code_insee"]==CODE and r["typecom"]=="COM"),
                    key=lambda r:r["debut_inclus"])
    expected=[
      ("Chemillé","1943-01-01","2013-01-01"),
      ("Chemillé-Melay","2013-01-01","2015-12-15"),
      ("Chemillé-en-Anjou","2015-12-15",None)
    ]
    if [(r["libelle"],r["debut_inclus"],r["fin_exclue"]) for r in episodes]!=expected:
        raise ValueError("Les trois épisodes COM doivent rester distincts")
    dates={r["date_effet"] for r in cog["lignes_mouvements_cog"]
           if r["mod"]=="32" and r["code_apres"]==CODE}
    if dates!={"2013-01-01","2015-12-15"}:
        raise ValueError("Dates MOD32 inattendues pour Chemillé")
    moves=cog["lignes_mouvements_cog"]
    for ancienne,nouvelle,date in [
       ("Chemillé","Chemillé-Melay","2013-01-01"),
       ("Chemillé-Melay","Chemillé-en-Anjou","2015-12-15")
    ]:
        if not any(m["mod"]=="32" and m["date_effet"]==date and
                   m["code_avant"]==CODE and m["code_apres"]==CODE and
                   m["libelle_avant"]==ancienne and m["libelle_apres"]==nouvelle and
                   m["typecom_avant"]=="COM" and m["typecom_apres"]=="COM"
                   for m in moves):
            raise ValueError("Transition COM historique non prouvée : "+ancienne)
    hits=[r for r in regional["communes"]
          if r["region"]=="52" and r["code"]==CODE]
    if (len(hits)!=1 or hits[0]["etat"]!="A_INSTRUIRE_PLUSIEURS_ARK" or
        len(hits[0]["preuves_RDF_exactMatch"])!=3):
        raise ValueError("Trois ARK Pactols concurrents exigés")
    candidates={r["ark"]:r for r in hits[0]["preuves_RDF_exactMatch"]}
    if set(candidates)!=set(ARKS.values()) or set(complement)!=set(ARKS.values()):
        raise ValueError("Les trois ARK historiques ne correspondent pas à la recette")
    for nom,ark in ARKS.items():
        c=candidates[ark]
        insee=[u for u in complement[ark]["exactMatch_tous"]
               if u.startswith(("http://id.insee.fr/geo/","https://id.insee.fr/geo/"))]
        if (c["prefLabels_fr"]!=[nom] or c["deprecie"] or c["remplace"] or
            c["insee_exactMatch"]!=[{"code":CODE,"famille":"commune","uri":URI}] or
            insee!=[URI] or complement[ark]["remplacements_explicites"]):
            raise ValueError("ARK Pactols mal attribué ou URI INSEE concurrente : "+ark)
    return {
      "schema":SCHEMA,"region":"pdl","millesime_cog":"2026-01-01",
      "source_registre":SOURCE,"source_RDF_Pactols_sha256":RDF_SHA,
      "alignements_publies_precedemment":1148,
      "nouveaux_alignements":1,
      "total_alignements_PDL_2026":1149,
      "communes_PDL_COG_2026":1228,
      "communes_a_instruire":79,
      "nouvelles_geometries":0,
      "liens_historiques_inferes":0,
      "alignements_Pactols_COG_valides_2026":[{
         "code_insee":CODE,"libelle_COG_2026":NOM,"libelle_pactols":NOM,
         "ark_pactols":ARKS[NOM],
         "ark_ancienne_Chemille":ARKS["Chemillé"],
         "ark_ancienne_Chemille_Melay":ARKS["Chemillé-Melay"],
         "uri_insee":URI,
         "predicat_source":"skos:exactMatch",
         "source_RDF_Pactols_sha256":RDF_SHA,
         "source_registre":SOURCE,
         "date_evenement_COG":"2015-12-15",
         "dates_MOD32":["2013-01-01","2015-12-15"],
         "nature_evenement_COG":"MOD32_CREATION_COMMUNE_NOUVELLE",
         "date_validation":"2026-11-18",
         "millesime_validation":2026,
         "statut":"correspondance_PDL_commune_nouvelle_validee_2026",
         "portee_chronologique":"2026_SEULEMENT",
         "relations_historiques_inferees":0
      }]
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("cog","base","uuid","lot01","rdf","cog-officiel","sortie"):
        p.add_argument("--"+name,required=True,type=Path)
    args=p.parse_args()
    if args.sortie.exists():
        raise ValueError("Ne pas écraser la publication")
    read=lambda f:json.loads(f.read_text(encoding="utf-8"))
    regional=audit(args.rdf,args.cog_officiel)
    extra=completer_rdf(args.rdf,set(ARKS.values()))
    d=publier(read(args.cog),read(args.base),read(args.uuid),
              read(args.lot01),regional,extra)
    args.sortie.parent.mkdir(parents=True,exist_ok=True)
    args.sortie.write_text(json.dumps(d,sort_keys=True,ensure_ascii=False,
                                     separators=(",",":"))+"\n",encoding="utf-8")
    print("PDL_CHEMILLE_1149_VALIDATION",json.dumps({
        "code":CODE,"ark":ARKS[NOM],"total":1149,"exceptions":79,
        "historiques_promus":0,"geometries":0},sort_keys=True))
if __name__=="__main__":
    main()
