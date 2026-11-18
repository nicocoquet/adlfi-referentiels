#!/usr/bin/env python3
"""Sélection conservatrice, non publiable, des collisions PDL après Chemillé."""
from __future__ import annotations
import argparse
import collections
import json
from pathlib import Path
from auditer_pactols_cog_regions_prioritaires_2026 import audit
from auditer_pdl_ark_multiples_2026 import construire
from qualifier_pdl_ark_multiples_2026 import qualifier
from auditer_pactols_polynesie_2026 import RDF_SHA

SCHEMA="adlfi.lieux.pdl.lot02.prequalification.2026.recette.v1"
BASE=["44005","44021","44029","44087","44163","49092"]
CODE_PREFIX="http://id.insee.fr/geo/commune/"

def preparer(rdf:Path,cog_source:Path,chrono:dict,publications:list[dict])->dict:
    publi=[entry for p in publications for entry in p["alignements_Pactols_COG_valides_2026"]]
    codes={p["code_insee"] for p in publi}
    arks={p["ark_pactols"] for p in publi}
    if len(publi)!=1149 or len(codes)!=1149 or len(arks)!=1149 or not set(BASE)<=codes:
        raise ValueError("La base publiée doit compter 1149 identités PDL uniques")
    regional=audit(rdf,cog_source)
    if regional.get("pactols",{}).get("sha256")!=RDF_SHA:
        raise ValueError("Empreinte RDF Pactols non conforme")
    multiples=construire(regional,chrono)
    qualif=qualifier(multiples,rdf)
    restants=[r for r in qualif["communes"] if r["code_COG_2026"] not in codes]
    if len(restants)!=54 or len({x["code_COG_2026"] for x in restants})!=54:
        raise ValueError("Le registre doit compter 54 collisions résiduelles")
    repart=collections.Counter(r["groupe_instruction"] for r in restants)
    if dict(repart)!={"CREATIONS_SUCCESSIVES":3,
                     "STATUT_HISTORIQUE_EXPLICITE":2,
                     "UN_LIBELLE_COMPATIBLE":49}:
        raise ValueError("Répartition des 54 dossiers inattendue : "+str(repart))
    mouvements=chrono["lignes_mouvements_cog"]
    periodes=chrono["periodes_com"]
    out=[]
    for row in restants:
        code=row["code_COG_2026"]
        nom=row["nom_COG_2026"]
        candidats=row["candidats"]
        conclusions=[]
        candidates_current=[c for c in candidats if
            c["prefLabels_fr"]==[nom] and c["compatibilite_libelle_sans_validation"]]
        if row["groupe_instruction"]!="UN_LIBELLE_COMPATIBLE":
            conclusions.append("CAS_COMPLEXE_OU_STATUT_HISTORIQUE")
        if len(candidats)!=2 or len(candidates_current)!=1:
            conclusions.append("UN_CANDIDAT_ACTUEL_UNIQUE_NON_ATTESTE")
        cand=candidates_current[0] if len(candidates_current)==1 else None
        old=[c for c in candidats if cand is None or c["ark"]!=cand["ark"]]
        if len(old)!=1 or len(old[0]["prefLabels_fr"])!=1:
            conclusions.append("ANCIEN_LIBELLE_NON_UNIQUE")
        def insee_propre(c:dict)->bool:
            urls=[u for u in c["autres_preuves_RDF"]["exactMatch_tous"]
                  if u.startswith(("http://id.insee.fr/geo/","https://id.insee.fr/geo/"))]
            return (urls==[CODE_PREFIX+code] and
                   c["insee_exactMatch_codes"]==[{
                       "code":code,"famille":"commune","uri":CODE_PREFIX+code}] and
                   not c["deprecie"] and not c["remplace"] and
                   not c["autres_preuves_RDF"]["remplacements_explicites"])
        if cand is None or not insee_propre(cand):
            conclusions.append("RDF_INSEE_ACTUEL_INSUFFISANT")
        if len(old)!=1 or not insee_propre(old[0]):
            conclusions.append("RDF_INSEE_ANCIEN_INSUFFISANT")
        dates=row["dates_MOD32"]
        if len(dates)!=1:
            conclusions.append("EVENEMENTS_SUCCESSIFS")
        date=dates[0] if len(dates)==1 else None
        if date and not any(m["date_effet"]==date and m["mod"]=="32" and
             m["code_apres"]==code and m["typecom_apres"]=="COM" and
             m["libelle_apres"]==nom for m in mouvements):
            conclusions.append("CREATION_COG_NON_ATTESTEE")
        old_label=old[0]["prefLabels_fr"][0] if len(old)==1 and len(old[0]["prefLabels_fr"])==1 else None
        if not (date and old_label and any(m["date_effet"]==date and
            m["mod"]=="32" and m["code_avant"]==code and
            m["code_apres"]==code and m["libelle_apres"]==old_label and
            m["typecom_avant"]=="COM" and m["typecom_apres"]=="COMD"
            for m in mouvements)):
            conclusions.append("PASSAGE_COM_VERS_COMD_NON_ATTESTE")
        courant=[p for p in periodes if p["code_insee"]==code and
                 p["typecom"]=="COM" and p["debut_inclus"]<="2026-01-01" and
                 (p["fin_exclue"] is None or p["fin_exclue"]>"2026-01-01")]
        if len(courant)!=1 or courant[0]["libelle"]!=nom or courant[0]["debut_inclus"]!=date:
            conclusions.append("ETAT_ACTUEL_OU_DATE_COG_NON_CONCORDANT")
        if any(c["ark"] in arks for c in candidats):
            conclusions.append("ARK_DEJA_PUBLIE")
        if not conclusions and cand is not None:
            etat="CANDIDAT_LOT02_A_VERIFIER"
        else:
            etat="INSTRUCTION_COMPLEMENTAIRE"
        out.append({
            "code_COG_2026":code,"nom_COG_2026":nom,"departement":row["departement"],
            "statut_prequalification":etat,
            "motifs_controle":sorted(set(conclusions)),
            "groupe_initial":row["groupe_instruction"],
            "date_creation_MOD32":date,
            "ark_candidat_2026":cand["ark"] if cand else None,
            "ark_historique_distinct":old[0]["ark"] if len(old)==1 else None,
            "libelle_historique":old_label,
            "ark_retenu":None,
            "decision_editoriale":"NON_PRISE",
            "publication":"NON_PUBLIE"
        })
    out.sort(key=lambda r:(r["statut_prequalification"]!="CANDIDAT_LOT02_A_VERIFIER",
                           r["departement"],r["code_COG_2026"]))
    counts=collections.Counter(r["statut_prequalification"] for r in out)
    return {"schema":SCHEMA,"statut":"RECETTE_NON_VALIDANTE",
            "source_RDF_Pactols_sha256":RDF_SHA,
            "total_initial_ARK_multiples":60,
            "deja_publies_depuis_cette_categorie":6,
            "restants":54,
            "repartition_initiale":dict(sorted(repart.items())),
            "groupes":dict(sorted(counts.items())),
            "liens_publies_avant_recette":1149,
            "nouveaux_alignements":0,
            "geometries_nouvelles":0,
            "successions_inferees":0,
            "dossiers":out}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ("rdf","cog-officiel","chronologie","base","uuid","lot01","chemille","sortie"):
        p.add_argument("--"+arg,required=True,type=Path)
    a=p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Écriture uniquement en recette nouvelle")
    read=lambda p:json.loads(p.read_text(encoding="utf-8"))
    d=preparer(a.rdf,a.cog_officiel,read(a.chronologie),
               [read(a.base),read(a.uuid),read(a.lot01),read(a.chemille)])
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(d,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("PDL_LOT02_BILAN",json.dumps(d["groupes"],sort_keys=True))
    for line in d["dossiers"]:
        print("PDL_LOT02_DOSSIER",json.dumps({
            "code":line["code_COG_2026"],"nom":line["nom_COG_2026"],
            "date":line["date_creation_MOD32"],"ark":line["ark_candidat_2026"],
            "ancienne":line["libelle_historique"],"ark_ancienne":line["ark_historique_distinct"],"etat":line["statut_prequalification"],
            "motifs":line["motifs_controle"]},sort_keys=True,ensure_ascii=False))
if __name__=="__main__":
    main()
