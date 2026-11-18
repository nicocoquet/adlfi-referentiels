#!/usr/bin/env python3
"""Dossier non validant des quatre créations successives PDL à ARK multiples."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from auditer_pactols_cog_regions_prioritaires_2026 import audit
from auditer_pdl_ark_multiples_2026 import construire
from qualifier_pdl_ark_multiples_2026 import qualifier

SCHEMA="adlfi.lieux.pdl.quatre-creations-successives.2026.recette.v1"
CAS={
 "49018":("Baugé-en-Anjou","NOM_CONSERVE_MAIS_SECONDE_CREATION_2016",
          ("2013-01-01","2016-01-01")),
 "49092":("Chemillé-en-Anjou","CANDIDAT_ACTUEL_DISTINCT_A_EVALUER",
          ("2013-01-01","2015-12-15")),
 "49160":("Ingrandes-le-Fresne-sur-Loire","AUCUN_ARK_AU_LIBELLE_2024",
          ("2016-01-01","2024-01-01")),
 "53161":("Montsûrs","LIBELLE_REEMPLOYE_AVANT_ET_APRES_2019",
          ("2017-01-01","2019-01-01"))
}
ARKS={
 "49018":{"26678/crtw3s8jkTOZ8","26678/pcrthdy1gGxlIV"},
 "49092":{"26678/pcrtL5GRFXn3Zs","26678/pcrtWU8rdgPSSH","26678/pcrtzDf0WnnRyr"},
 "49160":{"26678/pcrtD9YKBK1v7E","26678/pcrtQBSwT6fBDW"},
 "53161":{"26678/pcrt2VftxEe5uH","26678/pcrtzZXdqdUiXm"}
}

def rapport(rdf:Path,cog:Path,chronologie:dict)->dict:
    regional=audit(rdf,cog)
    multiples=construire(regional,chronologie)
    qualif=qualifier(multiples,rdf)
    index={x["code_COG_2026"]:x for x in qualif["communes"]}
    dates={}
    lignes=[]
    for code,(nom,probleme,attendues) in CAS.items():
        a=index.get(code)
        if not a or a["nom_COG_2026"]!=nom or a["groupe_instruction"]!="CREATIONS_SUCCESSIVES":
            raise ValueError("Dossier COG/Pactols non attendu : "+code)
        if set(c["ark"] for c in a["candidats"])!=ARKS[code]:
            raise ValueError("ARK Pactols concurrents inattendus : "+code)
        if tuple(a["dates_MOD32"])!=attendues:
            raise ValueError("Dates de création MOD32 incompatibles : "+code)
        com=[x for x in chronologie["periodes_com"] if
             x["code_insee"]==code and x["typecom"]=="COM"]
        com.sort(key=lambda x:x["debut_inclus"])
        if not com or com[-1]["libelle"]!=nom or com[-1]["fin_exclue"] is not None:
            raise ValueError("Épisode actuel de la commune absent : "+code)
        if len(com)<2:
            raise ValueError("Les phases de commune distinctes sont absentes : "+code)
        if code=="49018":
            # Le COG suit ici un intervalle de libellé 2013→2026,
            # bien que les mouvements portent une deuxième création en 2016.
            if com[-1]["debut_inclus"]!="2013-01-01":
                raise ValueError("Épisode Baugé inattendu")
        if code=="49160" and (com[-2]["libelle"]!="Ingrandes-Le Fresne sur Loire" or
                               com[-1]["debut_inclus"]!="2024-01-01"):
            raise ValueError("Les épisodes Ingrandes 2016/2024 sont confondus")
        if code=="53161" and ([x["libelle"] for x in com][-3:]!=
                               ["Montsûrs","Montsûrs-Saint-Céneré","Montsûrs"]):
            raise ValueError("Les deux Montsûrs ne sont pas séparés")
        if code=="49092" and ([x["libelle"] for x in com][-3:]!=
                               ["Chemillé","Chemillé-Melay","Chemillé-en-Anjou"]):
            raise ValueError("Les trois Chemillé ne sont pas séparés")
        lignes.append({
          "code_COG_2026":code,"libelle_COG_2026":nom,
          "probleme_editorial":probleme,"dates_MOD32":a["dates_MOD32"],
          "periodes_COM_libelles":com,
          "mouvements_COG":a["mouvements_COG_documentes"],
          "candidats_Pactols":a["candidats"],
          "ark_retenu":None,"decision_editoriale":"NON_PRISE","publication":"NON_PUBLIE"
        })
    return {
       "schema":SCHEMA,"statut":"RECETTE_NON_VALIDANTE",
       "sources":qualif["sources"],
       "bilan":{"communes_traitees":4,"ARK_examines":9,"validations":0,
                "geometries":0,"relations_historiques_inferees":0},
       "communes":lignes,
       "limites":[
          "L'année de création d'un concept ne prouve pas la continuité du périmètre.",
          "Un même libellé COG peut couvrir plusieurs créations MOD32 successives.",
          "La compatibilité du nom et du code ne suffit pas pour valider un ARK ancien sur l'état 2026.",
          "Les sources RDF historiques peuvent reprendre des définitions secondaires et ne prouvent pas seules une succession administrative."
       ]
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("rdf","cog","chronologie","sortie"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Sortie de recette uniquement, hors publication")
    chrono=json.loads(a.chronologie.read_text(encoding="utf-8"))
    x=rapport(a.rdf,a.cog,chrono)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,
                    indent=2)+"\n",encoding="utf-8")
    print("PDL_QUATRE_SUCCESSIONS_BILAN",json.dumps(x["bilan"],sort_keys=True))
    for row in x["communes"]:
        print("PDL_QUATRE_SUCCESSIONS_DOSSIER",json.dumps({
           "code":row["code_COG_2026"],"nom":row["libelle_COG_2026"],
           "probleme":row["probleme_editorial"],
           "periodes_COM":[{"nom":r["libelle"],"debut":r["debut_inclus"],
                             "fin":r["fin_exclue"]} for r in row["periodes_COM_libelles"]],
           "candidats":[{"ark":c["ark"],"pref":c["prefLabels_fr"],
                         "definitions":c["autres_preuves_RDF"]["definitions"]}
                        for c in row["candidats_Pactols"]]
        },ensure_ascii=False,sort_keys=True))
if __name__=="__main__":
    main()
