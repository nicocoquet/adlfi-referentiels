#!/usr/bin/env python3
"""Vérifier les 34 épisodes martiniquais publics contre le COG 2026 audité.

Ne crée ni relation temporelle Pactols ni géométrie.
"""
from __future__ import annotations
import argparse
import collections
import json
from pathlib import Path

EXPECTED_MOVES={
    ("1946-03-21","20"):32,
    ("1949-03-25","20"):2,
    ("1950-08-26","20"):2,
}


def verifier(audit:dict,public:dict)->dict:
    if audit.get("schema")!="adlfi.lieux.martinique.audit.cog-pactols-geom.v1":
        raise ValueError("Audit COG 2026 de Martinique non reconnu")
    if public.get("schema")!="adlfi.lieux.martinique.etats_cog_public.v1":
        raise ValueError("Chronologie publique Martinique non reconnue")
    expected=sorted((r["code"],r["libelle"],r["debut_inclus"],r["fin_exclue"] or "")
                    for r in audit["historique_codes_972"])
    actual=sorted(tuple(line.split("|")) for line in public["episodes"].splitlines())
    if len(expected)!=34 or expected!=actual:
        raise ValueError("Les 34 épisodes publics diffèrent de l'historique COG source")
    codes={r[0] for r in actual}
    if len(codes)!=34:
        raise ValueError("Des codes COG sont dupliqués")
    current={r["code_COG_2026"]:r["libelle_COG_2026"] for r in audit["communes"]}
    active={code:label for code,label,start,end in actual
            if start<="2026-01-01" and (not end or end>"2026-01-01")}
    if active!=current or len(current)!=34:
        raise ValueError("L'état actuel diverge du COG 2026")
    moves=collections.Counter((x["DATE_EFF"],x["MOD"])
                              for x in audit["mouvements_source_avec_code_972"])
    if moves!=EXPECTED_MOVES:
        raise ValueError("Événements martiniquais non conformes")
    exported={(x["date_effet"],x["modalite"]):x["lignes"]
              for x in public["mouvements_par_date"]}
    if exported!=EXPECTED_MOVES:
        raise ValueError("Événements publics diffèrent du COG")
    if (public["codes_historiques_non_courants"] or
        public["nouveaux_alignements_pactols"]!=0 or
        public["contours_historiques_publies"]!=0 or
        public["nouvelles_succession_inferrees"]!=0):
        raise ValueError("Publication d'inférences historiques non validées")
    return {"episodes":34,"codes":34,"mouvements":36,
            "annee_deux_creations":(1949,1950),
            "contours_historiques":0,"ark_historiques_supplementaires":0}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--audit",required=True,type=Path)
    p.add_argument("--public",required=True,type=Path)
    args=p.parse_args()
    a=json.loads(args.audit.read_text(encoding="utf-8"))
    d=json.loads(args.public.read_text(encoding="utf-8"))
    print(json.dumps(verifier(a,d),ensure_ascii=False,sort_keys=True,indent=2))
