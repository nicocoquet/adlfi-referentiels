#!/usr/bin/env python3
"""Audit non validant de 9 collisions historiques d'ARK Pactols en Pays de la Loire.

Le COG 2026 déjà versionné documente les évolutions administratives ; il ne
permet pas, à lui seul, d'assigner un ARK aux états territoriaux successifs.
"""
from __future__ import annotations
import argparse
import collections
import json
from pathlib import Path

from auditer_pactols_cog_regions_prioritaires_2026 import sha
from auditer_pactols_polynesie_2026 import RDF_SHA,analyser_rdf,norm
from qualifier_pdl_ark_multiples_2026 import completer_rdf

SCHEMA="adlfi.lieux.pdl.9-collisions-historiques.2026.audit.v1"
CODES={"49018":"Baugé-en-Anjou","49160":"Ingrandes-le-Fresne-sur-Loire",
       "49176":"Le Lion-d'Angers","49244":"Mauges-sur-Loire","53161":"Montsûrs",
       "53255":"Sainte-Suzanne-et-Chammes","72137":"Villeneuve-en-Perseigne",
       "72176":"Le Lude","85084":"Essarts-en-Bocage"}
PUBS=(
    "pactols-pdl-2026.json","pactols-pdl-uuid-resolus-2026.json",
    "pactols-pdl-communes-nouvelles-lot01-2026.json",
    "pactols-pdl-chemille-2026.json",
    "pactols-pdl-communes-nouvelles-lot02-2026.json",
    "pactols-pdl-oree-anjou-mod50-2026.json",
    "pactols-pdl-wikidata-p374-2026.json",
)
INSEE_ROOTS=("http://id.insee.fr/geo/","https://id.insee.fr/geo/")


def verifier_publications(data_dir:Path)->set[str]:
    read=lambda n:json.loads((data_dir/n).read_text(encoding="utf-8"))
    entries=[a for path in PUBS for a in read(path)["alignements_Pactols_COG_valides_2026"]]
    codes={x["code_insee"] for x in entries}
    arks={x["ark_pactols"] for x in entries}
    if len(entries)!=1212 or len(codes)!=1212 or len(arks)!=1212:
        raise ValueError("1212 correspondances PDL uniques requises")
    if set(CODES)&codes:
        raise ValueError("Une des 9 collisions est déjà publiée")
    return arks


def auditer(rdf:Path,cog:dict,data_dir:Path)->dict:
    if sha(rdf)!=RDF_SHA:raise ValueError("Le RDF Pactols th17 a changé")
    published_arks=verifier_publications(data_dir)
    if cog.get("region")!="pdl" or cog.get("millesime_cog")!=2026:
        raise ValueError("COG PDL 2026 incorrect")
    currents=[p for p in cog["periodes_com"] if
              p["typecom"]=="COM" and p["debut_inclus"]<="2026-01-01" and
              (p["fin_exclue"] is None or p["fin_exclue"]>"2026-01-01")]
    if len(currents)!=1228:
        raise ValueError("1228 communes COG PDL courantes attendues")
    bycode={x["code_insee"]:x for x in currents}
    if any(bycode.get(k,{}).get("libelle")!=v for k,v in CODES.items()):
        raise ValueError("Libellés courants COG des neuf dossiers modifiés")
    scan=analyser_rdf(rdf,CODES)
    arks={x["ark"] for code in CODES for x in scan["explicites"].get(code,[])}
    arks.update(x["ark"] for code in CODES for x in
                scan["lexicaux_sans_exactMatch_987"].get(code,[]))
    extra=completer_rdf(rdf,arks)
    rows=[]
    for code,label in sorted(CODES.items()):
        current=bycode[code]
        episodes=sorted((p for p in cog["periodes_com"] if
                         p["typecom"]=="COM" and p["code_insee"]==code),
                        key=lambda p:p["debut_inclus"])
        movements=sorted((m for m in cog["lignes_mouvements_cog"] if
                          m["code_avant"]==code or m["code_apres"]==code),
                         key=lambda m:(m["date_effet"],m["mod"],m["code_avant"],m["code_apres"]))
        mods=sorted({m["date_effet"] for m in movements if
                     m["mod"]=="32" and m["code_apres"]==code and
                     m["typecom_apres"]=="COM"})
        candidates=[]
        hits=scan["explicites"][code]
        lex=scan["lexicaux_sans_exactMatch_987"].get(code,[])
        if len(hits)<2:raise ValueError("Au moins deux ARK attendus pour "+code)
        for h in hits:
            more=extra[h["ark"]]
            all_insee=[u for u in more["exactMatch_tous"] if u.startswith(INSEE_ROOTS)]
            current_name=any(norm(a)==norm(label) for a in h["prefLabels_fr"])
            candidates.append({
              "ark":h["ark"],"prefLabels_fr":h["prefLabels_fr"],
              "altLabels_fr":h["altLabels_fr"],
              "porte_libelle_actuel":current_name,
              "deprecie":h["deprecie"],"remplace":h["remplace"],
              "skos_exactMatch_INSEE":all_insee,
              "skos_exactMatch_externes":[u for u in more["exactMatch_tous"]
                                           if u not in all_insee],
              "skos_closeMatch":more["closeMatch_tous"],
              "historique_RDF":more["notes_histoire"],
              "portee_RDF":more["notes_portee"],
              "definitions_RDF":more["definitions"],
              "remplacements_explicites":more["remplacements_explicites"],
              "ark_deja_publie":h["ark"] in published_arks
            })
        lexical=[{"ark":x["ark"],"prefLabels_fr":x["prefLabels_fr"],
                   "insee_lu":x["exactMatch_INSEE"]} for x in lex]
        if len(episodes)>=3:
            diagnostic="EPISODES_COM_SUCCESSIFS_MEME_CODE"
        elif len(mods)>1:
            diagnostic="CREATIONS_SUCCESSIVES_OU_EXTENSION"
        elif episodes[0]["libelle"]==current["libelle"]:
            diagnostic="NOM_INCHANGE_APRES_FUSION"
        else:
            diagnostic="CREATION_COMMUNE_NOUVELLE_AVEC_COLLISION_RDF"
        groups=collections.Counter({
            "ARK_courant_lexical":sum(x["porte_libelle_actuel"] for x in candidates),
            "ARK_historique_ou_non_concordant":sum(not x["porte_libelle_actuel"] for x in candidates),
        })
        rows.append({
          "code_COG_2026":code,"libelle_COG_2026":label,
          "debut_episode_COM_2026":current["debut_inclus"],
          "episodes_COM":[{"nom":p["libelle"],"debut":p["debut_inclus"],
                           "fin":p["fin_exclue"]} for p in episodes],
          "dates_MOD32":mods,
          "mouvements_COG":movements,
          "candidats_ARK_exactMatch":candidates,
          "candidats_ARK_lexicaux_sans_code":lexical,
          "effectifs_candidats":dict(groups),
          "diagnostic_COG":diagnostic,
          "alignement_ARK_2026":None,
          "decision_editoriale":"NON_PRISE",
          "publication":"NON_PUBLIE"
        })
    if len(rows)!=9:
        raise ValueError("Neuf dossiers doivent être documentés")
    statuses=collections.Counter(x["diagnostic_COG"] for x in rows)
    return {
        "schema":SCHEMA,"statut":"RECETTE_NON_VALIDANTE",
        "source_RDF_Pactols_sha256":RDF_SHA,
        "source_COG":"docs/data/lieux-chronologie/cog-pdl.json",
        "source_COG_mode":"DERIVE_VERSIONNE_2026",
        "couverture_PDL_avant":1212,"communes_PDL_COG_2026":1228,
        "nombre_dossiers":9,
        "groupes":dict(sorted(statuses.items())),
        "validations":0,"geometries_nouvelles":0,
        "liens_historiques_inferes":0,
        "dossiers":rows,
        "limites":[
          "Plusieurs épisodes administratifs peuvent partager un code et un libellé.",
          "Les exactMatch Pactols vers un code ne démontrent pas une continuité d'identité.",
          "Les libellés identiques avant/après fusion ne valent pas équivalence ARK.",
          "La recette ne décide ni de l'ARK actuel ni d'une succession historique."
        ],
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rdf",required=True,type=Path)
    parser.add_argument("--cog",required=True,type=Path)
    parser.add_argument("--data-dir",required=True,type=Path)
    parser.add_argument("--sortie",required=True,type=Path)
    a=parser.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Sortie de recette uniquement et jamais dans docs")
    data=auditer(a.rdf,json.loads(a.cog.read_text(encoding="utf8")),a.data_dir)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
                       encoding="utf8")
    print("PDL_NEUF_COLLISIONS_BILAN",json.dumps(data["groupes"],sort_keys=True))
    for x in data["dossiers"]:
        print("PDL_NEUF_COLLISIONS_DOSSIER",json.dumps({
          "code":x["code_COG_2026"],"nom":x["libelle_COG_2026"],
          "episodes":x["episodes_COM"],"dates_MOD32":x["dates_MOD32"],
          "diagnostic":x["diagnostic_COG"],
          "candidats":[{"ark":c["ark"],"pref":c["prefLabels_fr"],
                        "porte_libelle_actuel":c["porte_libelle_actuel"],
                        "insee":c["skos_exactMatch_INSEE"],
                        "autres":c["skos_exactMatch_externes"],
                        "notes":c["portee_RDF"]+c["historique_RDF"]}
                       for c in x["candidats_ARK_exactMatch"]],
          "lexicaux_sans_code":x["candidats_ARK_lexicaux_sans_code"]
        },sort_keys=True,ensure_ascii=False))

if __name__=="__main__":
    main()
