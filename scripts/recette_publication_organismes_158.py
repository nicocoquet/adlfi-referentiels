#!/usr/bin/env python3
"""Recette bloquante du JSON public Organismes 1.58 (A05f)."""
from __future__ import annotations
import json,sys
from pathlib import Path

SOURCE="AdlFI_referentiel_1-58_A05F_ARCHEO_ATLANTICA_CANDIDAT.xlsx"
SHA="6aa15da3019bc0a08987cd48631e95d09172d36b9fb80009b10a9636f1bf67d8"
COUNTS={"ORG-0756":(1,1,1),"ORG-0156":(3,2,9),"ORG-0004":(173,22,326),"ORG-0008":(46,18,270),
        "ORG-0192":(14,1,21),"ORG-0241":(7,1,32),
        "ORG-0348":(10,10,11),"ORG-0351":(2,1,2),
        "ORG-0451":(6,6,7),"SER-0041":(2,1,16)}

def validate(data):
    errors=[]
    def check(ok,msg):
        if not ok:errors.append(msg)
    p=data.get("provenance",{})
    check(p.get("source_filename")==SOURCE,"Nom du maître 1.58")
    check(p.get("source_sha256")==SHA,"SHA-256 du maître 1.58")
    check(p.get("exported_at_utc")=="2026-11-22T00:00:00+00:00","Horodatage reproductible")
    auth=data.get("authorities",[]);by={x["id"]:x for x in auth}
    rels=data.get("relations",[])
    check(len(auth)==len(by)==935,"935 autorités uniques")
    check(sum(a["kind"]=="ORG" for a in auth)==735,"735 ORG")
    check(sum(a["kind"]=="SER" for a in auth)==200,"200 SER")
    check(sum(a["validation"]["established"] is True for a in auth)==570,"570 autorités validées")
    check(sum(a["presentation"]["visible"] for a in auth)==683,"683 autorités visibles")
    check(len(rels)==600 and len({r["id"] for r in rels})==600,"600 relations uniques")
    for ident,n in COUNTS.items():
        use=by.get(ident,{}).get("usage",{})
        actual=(use.get("affiliations_linked"),use.get("affiliations_validated"),
                use.get("source_occurrences_linked"))
        check(actual==n,ident+" : compteurs attendus "+str(n))
    check(by.get("ORG-0348",{}).get("identifiers",{}).get("lab")=="UMR 7055",
          "PréTech : UMR historique")
    check(by.get("ORG-0348",{}).get("activity",{}).get("end")=="2021-12-31",
          "PréTech : date de fin historique inchangée")
    check(by.get("ORG-0539",{}).get("identifiers",{}).get("lab")=="UMR 8068",
          "TEMPS : UMR distincte")
    check(by.get("ORG-0351",{}).get("presentation",{}).get("visible") is False,
          "MAE : hors catalogue inchangé")
    check(by.get("ORG-0156",{}).get("activity",{}).get("end")=="2021-12-31",
          "Université Nantes historique : fin 2021")
    rel={r["id"]:r for r in rels}
    check(all(rel.get(i,{}).get("type")=="succession_partielle"
              and rel[i].get("target")=="ORG-0539"
              for i in ("REL-0144","REL-0145")),"Filiations historiques TEMPS inchangées")
    totals=data.get("totals",{})
    check(totals.get("service_sector_resolution")=={"public":197,"prive":3},
          "Secteurs SER inchangés")
    check(set(totals.get("service_level_unresolved_ids",[]))==
          {"SER-0178","SER-0202"},"Deux SER non résolus inchangés")
    check(totals.get("authorities")==935,"Total autorités cohérent")
    return errors

def main():
    p=Path(sys.argv[1]) if len(sys.argv)>1 else Path("docs/data/organismes.json")
    failures=validate(json.loads(p.read_text(encoding="utf-8")))
    for x in failures:print("ÉCHEC :",x,file=sys.stderr)
    if failures:return 1
    print("OK — 1.58 : 935 autorités, 569 validées, 600 relations, dix compteurs A05f")
    return 0

if __name__=="__main__":raise SystemExit(main())
