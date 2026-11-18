#!/usr/bin/env python3
"""Triangulation non validante Pactols exactMatch Wikidata P374 ↔ COG 2026.

Le téléchargement est séparé du rapport : on réanalyse DEUX FOIS le même JSON
Wikidata, et l'artefact conserve les identifiants révisionnels des éléments.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SCHEMA="adlfi.lieux.pdl.17-wikidata-p374.prequalification.2026.v1"
AUDIT_SCHEMA="adlfi.lieux.pdl.17-ark-sans-insee.prequalification.2026.v1"
QID=re.compile(r"^https://www\.wikidata\.org/wiki/(Q[1-9][0-9]*)$")
API="https://www.wikidata.org/w/api.php"
UA="AdlFI-Lieux-Pactols-COG-2026-audit/1.0 (https://github.com/nicocoquet/adlfi-referentiels)"


def liste_qids(audit:dict)->dict[str,str]:
    if audit.get("schema")!=AUDIT_SCHEMA or len(audit.get("dossiers",[]))!=17:
        raise ValueError("Le registre des 17 concepts contrôlés est requis")
    res={}
    for row in audit["dossiers"]:
        externes=row["rdf"]["exactMatch_tous"]
        hits=[QID.fullmatch(x) for x in externes]
        wikidata=[m.group(1) for m in hits if m]
        if len(wikidata)!=1:
            raise ValueError("Un seul exactMatch Wikidata attendu : "+row["code_insee"])
        if any("id.insee.fr/geo/" in uri for uri in externes):
            raise ValueError("Le candidat possède déjà une URI INSEE : "+row["code_insee"])
        if row["code_insee"] in res:
            raise ValueError("Code dupliqué")
        res[row["code_insee"]]=wikidata[0]
    if len(set(res.values()))!=17:
        raise ValueError("Un élément Wikidata par commune est requis")
    return res


def acquerir(qids:list[str],sortie:Path)->str:
    if sortie.exists() or "docs" in sortie.resolve().parts:
        raise ValueError("Fichier de preuve Wikidata hors docs, non existant")
    params=urllib.parse.urlencode({
       "action":"wbgetentities","ids":"|".join(sorted(qids)),
       "props":"info|claims|labels","languages":"fr|en","format":"json",
       "redirects":"no"
    })
    url=API+"?"+params
    req=urllib.request.Request(url,headers={
        "User-Agent":UA,"Accept":"application/json"})
    errors=[]
    for retry in range(3):
        try:
            with urllib.request.urlopen(req,timeout=25) as stream:
                if stream.status!=200:
                    raise ValueError("HTTP inattendu Wikidata : "+str(stream.status))
                raw=stream.read(12_000_000)
            data=json.loads(raw)
            entities=data.get("entities")
            if not isinstance(entities,dict) or set(entities)!=set(qids):
                raise ValueError("17 entités Wikidata non retournées")
            invalid={q:{"missing":e.get("missing"),"lastrevid":e.get("lastrevid")} for q,e in entities.items() if "missing" in e or "lastrevid" not in e}
            if invalid:
                raise ValueError("Entités Wikidata sans révision : "+repr(invalid))
            sortie.parent.mkdir(parents=True,exist_ok=True)
            sortie.write_bytes(raw)
            checksum=hashlib.sha256(raw).hexdigest()
            print("PDL_WIKIDATA_SNAPSHOT_SHA256",checksum)
            return checksum
        except (urllib.error.URLError,TimeoutError,OSError,ValueError,json.JSONDecodeError) as exc:
            errors.append(str(exc)[:160])
            if retry<2:time.sleep(3*(retry+1))
    raise RuntimeError("Acquisition Wikidata indisponible (aucun résultat non vérifié admis) : "+repr(errors))


def valeur(snak:dict):
    if snak.get("snaktype")!="value":
        return None
    return (snak.get("datavalue") or {}).get("value")


def en_date(v):
    if not isinstance(v,dict) or "time" not in v:return None
    m=re.match(r"^[+-](\d{4})-(\d{2})-(\d{2})T",v["time"])
    return "-".join(m.groups()) if m else None


def date_qualifier(claim,key):
    return sorted(filter(None,(en_date(valeur(s)) for s in
        (claim.get("qualifiers") or {}).get(key,[]))))


def p374_qualifies(entity,annee="2026-01-01"):
    all_rows=[]
    for claim in (entity.get("claims") or {}).get("P374",[]):
        val=valeur(claim.get("mainsnak") or {})
        if not isinstance(val,str):continue
        starts=date_qualifier(claim,"P580")
        ends=date_qualifier(claim,"P582")
        rank=claim.get("rank")
        active=(rank!="deprecated" and
                (not starts or min(starts)<=annee) and
                (not ends or max(ends)>=annee))
        all_rows.append({"code":val,"debut":starts,"fin":ends,
                         "rank":rank,"actif_2026":active})
    return sorted(all_rows,key=lambda x:(x["code"],x["debut"],x["fin"]))


def qids(claims,key):
    result=[]
    for claim in claims.get(key,[]):
        v=valeur(claim.get("mainsnak") or {})
        if isinstance(v,dict) and v.get("entity-type")=="item":
            result.append(v.get("id"))
    return sorted(set(x for x in result if x))


def qualifier(audit:dict,snapshot:dict)->dict:
    mapping=liste_qids(audit)
    entities=snapshot.get("entities")
    if not isinstance(entities,dict) or set(entities)!=set(mapping.values()):
        raise ValueError("Snapshot Wikidata incomplet")
    dossiers=[]
    for row in sorted(audit["dossiers"],key=lambda r:r["code_insee"]):
        code=row["code_insee"]
        qid=mapping[code]
        entity=entities[qid]
        if entity.get("id")!=qid or "lastrevid" not in entity:
            raise ValueError("Élément Wikidata/révision incohérent : "+qid)
        p374=p374_qualifies(entity)
        active=[x["code"] for x in p374 if x["actif_2026"]]
        props=entity.get("claims") or {}
        p31=qids(props,"P31")
        inception=sorted(filter(None,(en_date(valeur(x.get("mainsnak") or {}))
            for x in props.get("P571",[]))))
        label_fr=((entity.get("labels") or {}).get("fr") or {}).get("value")
        label_en=((entity.get("labels") or {}).get("en") or {}).get("value")
        if len(active)==1 and active[0]==code:
            verdict="P374_CONCORDE_COG_2026"
        elif not active:
            verdict="P374_ABSENT_OU_NON_ACTIF"
        else:
            verdict="P374_CONTRADICTOIRE_OU_MULTIPLE"
        dossiers.append({
          "code_COG_2026":code,"libelle_COG_2026":row["libelle_COG_2026"],
          "ark_pactols":row["ark_candidat"],"URI_Wikidata":"https://www.wikidata.org/wiki/"+qid,
          "qid":qid,"Wikidata_lastrevid":entity["lastrevid"],
          "libelle_fr_Wikidata":label_fr,"libelle_en_Wikidata":label_en,
          "insee_P374_tous":p374,"insee_P374_actifs_2026":active,
          "P31_instances":p31,"dates_P571":inception,
          "date_creation_COG":row["debut_communale_COG_2026"],
          "mouvements_MOD32_COG":len(row["creation_mod32_COG"]),
          "homonymes_Pactols":row["homonymes_prefLabel_RDF"],
          "classement":verdict,
          "source_Pactols_relation":"skos:exactMatch",
          "source_Wikidata_code":"P374 (Insee municipality code)",
          "portee_decision":"2026_SEULEMENT",
          "decision_editoriale":"NON_PRISE","publication":"NON_PUBLIE"
        })
    from collections import Counter
    groups=Counter(x["classement"] for x in dossiers)
    return {
      "schema":SCHEMA,"statut":"RECETTE_NON_VALIDANTE",
      "source_RDF":"Pactols th17 du 22 juillet 2026 SHA-256 épinglé",
      "source_Wikidata":"API wbgetentities; les lastrevid sont conservés",
      "source_COG":"docs/data/lieux-chronologie/cog-pdl.json (dérivé 2026)",
      "nombre_ARK":17,"couverture_PDL_avant":1195,
      "groupes":dict(sorted(groups.items())),
      "nouvelles_validations":0,"liens_historiques_inferes":0,
      "geometries_nouvelles":0,"dossiers":dossiers
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--audit",type=Path,required=True)
    p.add_argument("--snapshot",type=Path,required=True)
    p.add_argument("--sortie",type=Path)
    p.add_argument("--acquerir",action="store_true")
    a=p.parse_args()
    source=json.loads(a.audit.read_text(encoding="utf8"))
    mapping=liste_qids(source)
    if a.acquerir:
        acquerir(list(mapping.values()),a.snapshot)
        return
    if a.sortie is None or a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Sortie de recette nouvelle hors docs requise")
    wikidata=json.loads(a.snapshot.read_text(encoding="utf8"))
    result=qualifier(source,wikidata)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print("PDL_17_WIKIDATA_BILAN",json.dumps(result["groupes"],sort_keys=True))
    for row in result["dossiers"]:
        print("PDL_17_WIKIDATA_DOSSIER",json.dumps({
          "code":row["code_COG_2026"],"nom":row["libelle_COG_2026"],
          "qid":row["qid"],"revid":row["Wikidata_lastrevid"],
          "p374_actif":row["insee_P374_actifs_2026"],
          "p374_complet":row["insee_P374_tous"],"instances":row["P31_instances"],
          "inception":row["dates_P571"],"classement":row["classement"],
        },ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
