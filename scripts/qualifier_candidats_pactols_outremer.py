#!/usr/bin/env python3
"""Trier les associations lexicales Pactols–COG ultramarines (sans alignement).

Le RDF intégral produit un jeu exhaustif d'INDICES : certaines formes
qualifiées renvoient à des lieux métropolitains homonymes. Conserver les
371 lignes sources ; séparer les candidats à instruire des rapprochements
lexicaux à écarter pour la priorité de traitement.
"""
from __future__ import annotations
import argparse
import collections
import csv
import json
import re
import unicodedata
from pathlib import Path

DROM_CTX={
 "971":{"guadeloupe","antilles francaises"},
 "972":{"martinique","antilles francaises"},
 "973":{"guyane","guyane francaise"},
 "974":{"la reunion","reunion","ile de la reunion"},
 "976":{"mayotte"},
}
COMER_CTX={
 "975":{"saint pierre et miquelon"},
 "977":{"saint barthelemy","antilles francaises"},
 "978":{"saint martin","antilles francaises"},
 "981":{"ile des faisans"},
 "984":{"taaf","terres australes et antarctiques francaises","iles australes"},
 "986":{"wallis et futuna","wallis","futuna"},
 "987":{"polynesie","polynesie francaise"},
 "988":{"nouvelle caledonie"},
 "989":{"clipperton","la passion clipperton"},
}
CATEGORIES=(
 "code_et_libelle","code_seul_ou_nom_different",
 "nom_exact_sans_code","nom_qualifie_compatible",
 "qualificatif_a_verifier","qualificatif_incompatible",
)

def norm(s):
 s=str(s or "").replace("œ","oe").replace("Œ","Oe")
 s=unicodedata.normalize("NFKD",s).casefold()
 s="".join(c for c in s if unicodedata.category(c)!="Mn")
 return " ".join(re.sub(r"[^a-z0-9]+"," ",s).split())

def lire(path):
 with Path(path).open(encoding="utf-8-sig",newline="") as f:
  reader=csv.DictReader(f,delimiter=";")
  if not reader.fieldnames:raise ValueError("CSV vide")
  return list(reader)

def contextes(row):
 if row["famille"]=="DROM":
  return DROM_CTX[row["code_cog"][:3]]
 code=row["code_parent_comer"] if row["niveau"]=="subdivision" else row["code_cog"]
 return COMER_CTX.get(code,set())

def qualificatifs(row):
 out=set()
 for key in ("pref_fr","alt_fr","hidden_fr"):
  for libelle in json.loads(row[key]):
   m=re.search(r"\(([^()]*)\)\s*$",libelle)
   if m:out.add(norm(m.group(1)))
 return sorted(out)

def classifier(row):
 signals=set(row["signaux"].split("|"))
 code="lien_insee_code_meme_valeur" in signals
 exact=bool(signals & {"pref_fr_exact","alt_fr_exact"})
 quals=qualificatifs(row)
 contexte=contextes(row)
 compatible=any(q in contexte for q in quals)
 incompatible=bool(quals) and not compatible
 if code:
  category="code_et_libelle" if exact or compatible else "code_seul_ou_nom_different"
 elif exact:category="nom_exact_sans_code"
 elif compatible:category="nom_qualifie_compatible"
 elif incompatible:category="qualificatif_incompatible"
 else:category="qualificatif_a_verifier"
 return {**row,
   "qualif":category,
   "qualificatifs_detectes":" | ".join(quals),
   "contextes_attendus":" | ".join(sorted(contexte)),
   "alerte_qualificatif":("contexte_incompatible_avec_code"
                         if incompatible and code else
                         "non_compatible" if incompatible else "aucune"),
   "a_examiner_prioritairement":"non" if category=="qualificatif_incompatible" else "oui",
   "statut_decision":"A_INSTRUIRE_NON_VALIDE",
 }

def produire(candidats,cibles,sortie):
 source=lire(candidats); targets=lire(cibles)
 required={"cible_id","famille","niveau","code_cog","code_parent_comer",
           "pref_fr","alt_fr","hidden_fr","signaux","ark_candidat",
           "correspondance_code_insee_meme_valeur"}
 if not source or any(not required<=set(row) for row in source):
  raise ValueError("Champs des candidats manquants")
 byid={r["cible_id"]:r for r in targets}
 if len(byid)!=len(targets) or any(r["cible_id"] not in byid for r in source):
  raise ValueError("Cible absente ou en doublon")
 qual=[classifier(r) for r in source]
 qual.sort(key=lambda r:(r["cible_id"],CATEGORIES.index(r["qualif"]),r["ark_candidat"]))
 grouped=collections.defaultdict(list)
 for r in qual:grouped[r["cible_id"]].append(r)
 summary=[]
 for t in sorted(targets,key=lambda r:r["cible_id"]):
  rows=grouped[t["cible_id"]]
  eligible=[r for r in rows if r["a_examiner_prioritairement"]=="oui"]
  summary.append({**t,"nb_candidats_bruts":len(rows),
    "nb_pistes_a_instruire":len(eligible),
    "nb_qualificatifs_incompatibles":len(rows)-len(eligible),
    "nb_mentions_insee_meme_code":sum(
        r["correspondance_code_insee_meme_valeur"]=="oui" for r in rows),
    "statut":("sans_signal_snapshot" if not rows else
              "indices_multiples_ou_insuffisants" if not eligible or len(eligible)>1
              else "piste_unique_a_examiner"),
    "decision_editoriale":"A_FAIRE"})
 dest=Path(sortie)
 if "docs" in dest.resolve().parts:raise ValueError("Résultat de recette interdit dans docs/")
 if dest.resolve().is_relative_to(Path(candidats).resolve().parent):
  raise ValueError("Les résultats doivent être dans un autre dossier que les sources")
 dest.mkdir(parents=True,exist_ok=True)
 def ecrire(name,rows):
  with (dest/name).open("w",encoding="utf-8-sig",newline="") as f:
   writer=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=";")
   writer.writeheader();writer.writerows(rows)
 ecrire("qualification_pistes_Pactols_ultramarines.csv",qual)
 ecrire("synthese_233_apres_filtre_contextuel.csv",summary)
 report={
  "schema":"adlfi.lieux.outremer.pactols.qualification.v1",
  "statut":"RECETTE_NON_VALIDANTE_NON_PUBLIEE",
  "cibles":len(targets),"associations_brutes":len(source),
  "associations_par_qualification":dict(sorted(collections.Counter(
       r["qualif"] for r in qual).items())),
  "associations_qualificatif_incompatible":sum(
      r["qualif"]=="qualificatif_incompatible" for r in qual),
  "associations_a_examiner":sum(
      r["a_examiner_prioritairement"]=="oui" for r in qual),
  "cibles_avec_piste_a_instruire":sum(
      r["nb_pistes_a_instruire"]>0 for r in summary),
  "cibles_sans_piste_a_instruire":[
      r["cible_id"] for r in summary if not r["nb_pistes_a_instruire"]],
  "cibles_avec_plusieurs_pistes":sum(r["nb_pistes_a_instruire"]>1 for r in summary),
  "cibles_sans_signal_rdf":sum(r["nb_candidats_bruts"]==0 for r in summary),
  "nouveaux_alignements_valides":0,
  "limite":"Une URI INSEE présente dans skos:exactMatch n'est pas une validation AdlFI. "
           "Les formes qualifiées non compatibles restent conservées dans le journal "
           "des candidats bruts ; aucun identifiant n'est attribué automatiquement.",
 }
 (dest/"rapport_qualification_pactols_outremer.json").write_text(
     json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
 return report

if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--candidats",required=True,type=Path)
 p.add_argument("--cibles",required=True,type=Path)
 p.add_argument("--sortie",required=True,type=Path)
 opts=p.parse_args()
 print(json.dumps(produire(**vars(opts)),ensure_ascii=False,indent=2))
