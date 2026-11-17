#!/usr/bin/env python3
"""Vérifier les décisions 2026 NC/SPM/Dembeni contre le RDF Pactols épinglé.

Aucune validation RDF n'est inférée à partir de la seule confirmation d'ARK.
Dembeni est contrôlée séparément ; le rapport reste non publiant.
"""
from __future__ import annotations
import argparse,csv,json
from collections import Counter
from pathlib import Path
from auditer_pactols_polynesie_2026 import analyser_rdf,sha,RDF_SHA

EXPECTED={
 "97501":"26678/pcrtQAMzeGHldU",
 "97502":"26678/pcrtYQmFfwxLq8",
 "97607":"26678/crtZcuFSJVYZU",
 "98809":"26678/pcrti4LqTHByEs",
}
HEAD=("code_insee","libelle_COG_2026","ark_pactols","uri_insee",
      "predicat_source","source","statut_validation","portee_COG",
      "qualification","note_editoriale")
ARK_CONFIRM="ARK_CONFIRME_EDITORIALEMENT_LIEN_NON_CERTIFIE_PAR_EXACTMATCH"

def lire_csv(path:Path,index:dict)->dict:
    with path.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f,delimiter=";")
        if tuple(reader.fieldnames or ())!=HEAD:
            raise ValueError("Colonnes du registre inattendues")
        rows=list(reader)
    if len(rows)!=36 or any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError("Le registre doit contenir 36 décisions complètes")
    names={}
    for group,raw in index["communes"].items():
        names.update(dict(s.split("|",1) for s in raw.splitlines()))
    expected_codes={"97501","97502","97607"}|set(dict(s.split("|",1)
                     for s in index["communes"]["988"].splitlines()))
    seen=set()
    all_arks=set(index["pactols_valides"].values()) | set(
        index["pactols_collectivites_valides"].values())
    for row in rows:
        code=row["code_insee"];ark=row["ark_pactols"]
        if (code not in expected_codes or code in seen or
            names[code]!=row["libelle_COG_2026"] or
            row["uri_insee"]!="http://id.insee.fr/geo/commune/"+code or
            row["portee_COG"]!="2026-01-01" or
            ark in all_arks or
            (code in EXPECTED and ark!=EXPECTED[code])):
            raise ValueError("Décision incohérente : "+code)
        if (row["predicat_source"]!="skos:exactMatch" or
            row["statut_validation"]!="VALIDE_ADLFI_2026" or
            row["source"]!="Pactols_Lieux_th17_20260722.rdf" or
            row["qualification"]!=
             ("EXCEPTION_EDITORIALE_LIBELLE_ILE" if code in ("97502","98809")
              else "CONFORME_REGLE")):
            raise ValueError("Décision RDF 2026 non conforme : "+code)
        if code=="97607" and index["ark_confirmes_non_valides"].get(code)!=ark:
            raise ValueError("Dembeni : ARK confirmé historique non conservé")
        seen.add(code);all_arks.add(ark)
    if seen!=expected_codes:
        raise ValueError("Liste de codes incomplète")
    return {x["code_insee"]:x for x in rows}

def controle(rdf:Path,index_file:Path,registre:Path)->dict:
    if sha(rdf)!=RDF_SHA:
        raise ValueError("Pactols RDF source non conforme")
    index=json.loads(index_file.read_text(encoding="utf-8"))
    if len(index["pactols_valides"])!=176 or len(index["pactols_collectivites_valides"])!=4:
        raise ValueError("Socle publié différent des 176+4 attendus")
    rows=lire_csv(registre,index)
    names={c:r["libelle_COG_2026"] for c,r in rows.items()}
    scan=analyser_rdf(rdf,names)
    results=[]
    for code,r in sorted(rows.items()):
        hits=scan["explicites"][code]
        evidence=next((h for h in hits if h["ark"]==r["ark_pactols"]),None)
        exact_unique=(len(hits)==1 and evidence is not None and
            evidence["codes_communaux_cites"]==[code] and
            evidence["insee_exactMatch"]==[{"uri":r["uri_insee"],
               "famille":"commune","code":code}] and
            not evidence["deprecie"] and not evidence["remplace"])
        if not exact_unique:
            raise ValueError("exactMatch RDF non unique / divergent : "+code)
        results.append({
            "code":code,"ark":r["ark_pactols"],"preuve_RDF_exactMatch_unique":exact_unique,
            "libelles_RDF":evidence["prefLabels_fr"] if evidence else [],
            "altLabels_RDF":evidence["altLabels_fr"] if evidence else [],
            "qualification":r["qualification"],
            "statut_decision":r["statut_validation"],
        })
    return {
       "schema":"adlfi.lieux.decisions.nc-spm-dembeni.2026.audit.v1",
       "statut":"RECETTE_NON_PUBLIANTE",
       "source_rdf_sha256":RDF_SHA,
       "decisions":results,
       "bilan":{
          "decisions":36,
          "exactMatch_valides_sur_source":sum(r["preuve_RDF_exactMatch_unique"] for r in results),
          "Dembeni_exactMatch_retrouve":results[[r["code"] for r in results].index("97607")]["preuve_RDF_exactMatch_unique"],
          "correspondances_publiees_au_socle":176,
          "nouvelles_correspondances_publiees":0,
       },
    }
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("rdf","index","registre","sortie"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("rapport uniquement hors docs")
    r=controle(a.rdf,a.index,a.registre)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("VALIDATIONS_OUTREMER",json.dumps(r["bilan"],ensure_ascii=False))
    print("DEMBENI",json.dumps([x for x in r["decisions"] if x["code"]=="97607"],ensure_ascii=False))
if __name__=="__main__":main()
