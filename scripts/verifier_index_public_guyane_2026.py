#!/usr/bin/env python3
"""Comparer l'index public Guyane aux 41 observations et mouvements COG officiels.

Aucune génération de géométrie. Échec si le JSON public diffère de la recette.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path


def verifier(audit: dict, public: dict) -> dict:
    if audit.get("schema")!="adlfi.lieux.guyane.audit.cog-pactols-geom.v1":
        raise ValueError("Recette COG Guyane d'origine incompatible")
    if public.get("schema")!="adlfi.lieux.guyane.etats_cog_public.v1":
        raise ValueError("Index public Guyane incompatible")
    raw=audit["historique_codes_973"]
    expected=sorted(
        (row["code"],row["libelle"],row["debut_inclus"],row["fin_exclue"] or "")
        for row in raw
    )
    actual=sorted(tuple(line.split("|")) for line in public["episodes"].splitlines())
    if len(expected)!=41 or expected!=actual:
        missing=sorted(set(expected)-set(actual))[:3]
        extra=sorted(set(actual)-set(expected))[:3]
        raise ValueError(f"Épisodes COG différents : {missing=!r} {extra=!r}")
    codes={x[0] for x in actual}
    if len(codes)!=26:
        raise ValueError("26 codes communaux Guyane attendus")
    from_2026={
        r["code_COG_2026"]:r["libelle_COG_2026"]
        for r in audit["communes"]
    }
    active={}
    for code,label,start,end in actual:
        if start<="2026-01-01" and (not end or end>"2026-01-01"):
            if code in active:raise ValueError("Doublon de commune au 1er janvier 2026")
            active[code]=label
    if active!=from_2026 or len(active)!=22:
        raise ValueError("Le COG publié n'est pas celui de 2026")
    mods=collections.defaultdict(list)
    for move in audit["mouvements_source_avec_code_973"]:
        if move["DATE_EFF"]=="1969-03-27" and move["MOD"]=="31" and (
            move["COM_AV"]!=move["COM_AP"]
        ):
            mods[move["COM_AV"]].append(move["COM_AP"])
    expected_old={"97351","97354","97355","97359"}
    if set(mods)!=expected_old or any(len(v)!=1 for v in mods.values()):
        raise ValueError("Les quatre fusions COG 1969 ont changé")
    sources={
        x["code_insee_cite"]:x
        for x in audit["bilan"]["source_Pactols_stats"]["liens_insee_non_courants"]
    }
    if set(sources)!=expected_old:raise ValueError("Concepts historiques Pactols différents")
    old=public["anciennes"]
    if len(old)!=4 or {x["code"] for x in old}!=expected_old:
        raise ValueError("Autorités historiques publiées incomplètes")
    for x in old:
        code=x["code"];src=sources[code]
        if x["ark_candidat"]!=src["ark"] or (
            x["code_destination_mouvement_COG_1969"]!=mods[code][0]) or (
            src["predicat"]!="exactMatch") or src["concept_deprecie"] or (
            src["concept_remplace"]) or (
            src["codes_communes_INSEE_exactMatch"]!=[code]):
            raise ValueError("Identité ancienne Pactols/COG non sourcée : "+code)
    if public["contours_historiques_publies"]!=0 or (
       public["nouvelles_relations_pactols_validees"]!=0):
        raise ValueError("L'historique ne doit valider ni contour ni Pactols")
    return {"episodes_verifies":41,"codes_verifies":26,"communes_actuelles":22,
            "communes_anciennes":4,"fusions_COG_verifiees":4,
            "nouvelles_geometries":0,"nouvelles_correspondances_pactols":0}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--audit",type=Path,required=True)
    p.add_argument("--public",type=Path,required=True)
    args=p.parse_args()
    a=json.loads(args.audit.read_text(encoding="utf-8"))
    b=json.loads(args.public.read_text(encoding="utf-8"))
    print(json.dumps(verifier(a,b),ensure_ascii=False,sort_keys=True,indent=2))
