#!/usr/bin/env python3
"""Rapprocher 14 événements COG documentés avec les concepts du Pactols intégral.

Toutes les sorties sont des candidatures de RECETTE, jamais des validations.
Le rapprochement n'accepte pas un exactMatch de code Insee seul comme
preuve d'identité entre une ancienne commune et la commune réceptrice.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

SHA_CANDIDATS = "24945819b4f587bcaf9c4b63001c3859069c955389a253494bfdf9994e780c6e"
FIELDS = ("ark_source","libelle_source","code_source","code_cible_insee",
          "libelle_cible_cog","date_evenement","modalite_cog","preuve_cog",
          "ark_cible_candidat","pref_fr_cible","types_preuves_pactols",
          "code_insee_sur_ark_cible","niveau_instruction",
          "autres_ark_avec_code","validation_adlfi")

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for buf in iter(lambda:f.read(1<<20),b""):
            h.update(buf)
    return h.hexdigest()

def lire(path,cols):
    with Path(path).open("r",encoding="utf-8-sig",newline="") as f:
        rd=csv.DictReader(f,delimiter=";")
        if not set(cols)<=set(rd.fieldnames or []):
            raise ValueError("Colonnes de source manquantes: "+str(path))
        return list(rd)

def classer(candidats):
    """Choisir un seul libellé présent, jamais un seul code sans nom."""
    def score(r):
        s=set(r["signaux"].split("|"))
        if "prefLabel_fr_exact" in s and "exactMatch_insee_code" in s:return (4,"prefLabel_et_code")
        if "prefLabel_fr_qualifie" in s and "exactMatch_insee_code" in s:return (3,"prefLabel_qualifie_et_code")
        if "altLabel_fr_exact" in s and "exactMatch_insee_code" in s:return (3,"altLabel_et_code")
        if "prefLabel_fr_exact" in s:return (2,"prefLabel_seul_code_absent")
        if "prefLabel_fr_qualifie" in s:return (1,"prefLabel_qualifie_code_absent")
        if "altLabel_fr_exact" in s:return (1,"altLabel_seul_code_absent")
        return (0,"code_seul_insuffisant")
    scores=[(score(r),r) for r in candidats if r["ark_candidat"]]
    if not scores:return None,"aucun_candidat_de_concept"
    maxscore=max(a[0][0] for a in scores)
    best=[(a,r) for a,r in scores if a[0]==maxscore]
    if maxscore==0:return None,"code_seul_insuffisant"
    if len(best)!=1:return None,"plusieurs_concepts_lexicaux_ambigus"
    return best[0][1],best[0][0][1]

def produire(dossiers,candidats,sortie):
    if sha(candidats)!=SHA_CANDIDATS:
        raise ValueError("Les 16 candidats ne sont pas ceux du RDF th17 du 22 juillet 2026")
    originals=lire(dossiers,("ark_source","libelle_source","code_source",
                            "code_cible_insee","libelle_cible_cog",
                            "date_evenement","modalite_cog","preuve_cog"))
    concepts=lire(candidats,("code_cible_insee","libelle_cible_cog",
                              "ark_candidat","pref_fr","signaux","codes_insee_exactmatch"))
    if len(originals)!=14 or len({r["ark_source"] for r in originals})!=14 or len(concepts)!=16:
        raise ValueError("Périmètre documentaire de 14 dossiers/16 concepts modifié")
    bycode=collections.defaultdict(list)
    for c in concepts:bycode[c["code_cible_insee"]].append(c)
    if len(bycode)!=8 or {r["code_cible_insee"] for r in originals}!=set(bycode):
        raise ValueError("Huit destinations attendues")
    out=[];cnt=collections.Counter();cible_selected={}
    for r in sorted(originals,key=lambda x:(x["code_cible_insee"],x["ark_source"])):
        code=r["code_cible_insee"]
        if not all(c["libelle_cible_cog"]==r["libelle_cible_cog"] for c in bycode[code]):
            raise ValueError("Destination administrative discordante "+code)
        chosen,statut=classer(bycode[code])
        cnt[statut]+=1
        candidate_code=json.loads(chosen["codes_insee_exactmatch"]) if chosen else []
        if chosen:
            if code in cible_selected and cible_selected[code]!=chosen["ark_candidat"]:
                raise ValueError("Destination multiple pour un même code")
            cible_selected[code]=chosen["ark_candidat"]
        code_arks=sorted({c["ark_candidat"] for c in bycode[code]
                           if "exactMatch_insee_code" in c["signaux"].split("|")})
        out.append({**r,
            "ark_cible_candidat":chosen["ark_candidat"] if chosen else "",
            "pref_fr_cible":chosen["pref_fr"] if chosen else "",
            "types_preuves_pactols":chosen["signaux"] if chosen else "aucun_libelle_concordant",
            "code_insee_sur_ark_cible":"oui" if code in candidate_code else "non",
            "niveau_instruction":statut,
            "autres_ark_avec_code":json.dumps(code_arks,ensure_ascii=False),
            "validation_adlfi":"non_valide"})
    if sum(v for k,v in cnt.items() if k not in
           ("code_seul_insuffisant","aucun_candidat_de_concept","plusieurs_concepts_lexicaux_ambigus"))!=13:
        raise ValueError("13 candidatures lexicales attendues")
    if cnt != {"prefLabel_et_code":9,"prefLabel_qualifie_et_code":1,
               "prefLabel_seul_code_absent":3,"code_seul_insuffisant":1}:
        raise ValueError("Répartition de preuve incorrecte "+str(cnt))
    if not (out[-1]["code_cible_insee"]=="71566" and not out[-1]["ark_cible_candidat"]):
        raise ValueError("Verdun-Ciel doit rester sans candidat dans ce snapshot")

    dest=Path(sortie)
    if any((dest/n).resolve() in {Path(dossiers).resolve(),Path(candidats).resolve()} for n in
           ("rapprochement-bfc-14-th17.csv","rapport-rapprochement-bfc-th17.json")):
        raise ValueError("Écrasement de sources interdit")
    dest.mkdir(parents=True,exist_ok=True)
    with (dest/"rapprochement-bfc-14-th17.csv").open("w",encoding="utf-8-sig",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=FIELDS,delimiter=";",extrasaction="ignore")
        wr.writeheader();wr.writerows(out)
    report={"etat":"recette_non_validante","snapshot_pactols":"2026-07-22",
            "dossiers_documentaires":len(out),"communes_receptices":len(bycode),
            "dossiers_avec_concept_cible_lexical":13,
            "dossiers_sans_concept_cible":1,
            "communes_avec_concept_cible":len(cible_selected),
            "niveaux_preuve":dict(sorted(cnt.items())),
            "sources_sha256":{"dossiers":sha(dossiers),"candidats_pactols":sha(candidats)},
            "dossier_ouvert":"Ciel (71131) -> Verdun-Ciel (71566) : code exactMatch sur Verdun-sur-le-Doubs, mais aucun prefLabel/altLabel correspond au nom de la commune nouvelle",
            "nouveaux_liens_valides":0,"geometries_historiques":0,
            "reserve":"Aucune équivalence ou relation de succession validée ; les 13 ARK sont des candidats à instruire, les états COG sont datés."}
    (dest/"rapport-rapprochement-bfc-th17.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for n in ("dossiers","candidats","sortie"):p.add_argument("--"+n,type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(produire(a.dossiers,a.candidats,a.sortie),ensure_ascii=False,indent=2))
