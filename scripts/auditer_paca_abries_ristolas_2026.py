#!/usr/bin/env python3
"""Abriès-Ristolas : examen documentaire de l'ARK lexical sans exactMatch Insee.

N'effectue aucune validation : sépare la commune nouvelle COG 05001, l'ancienne
commune Abriès au code conservé et le concept Pactols contemporain nommé.
Contrôle les 50 556 concepts de l'instantané Pactols du 22 juillet 2026.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from auditer_pactols_polynesie_2026 import ARK, RDF, SKOS, OWL, DCT, XML, RDF_SHA, RDF_COMMIT, norm
from auditer_paca_trois_renommages_rdf_2026 import sha256

SCHEMA="adlfi.lieux.paca.abries_ristolas.2026.audit.v1"
OLD="26678/pcrtGQ7nGPZN7K"
NEW="26678/pcrtm96gvvfnwmggc9z0wrxn"
COG="05001"
OLD_LABEL="Abriès"
NEW_LABEL="Abriès-Ristolas"
OTHER="Ristolas"
EXPECTED_COUNT=50556
SKOS_ELEMENTS=("prefLabel","altLabel","hiddenLabel","historyNote","changeNote","scopeNote",
               "definition","editorialNote","notation")
SKOS_REFS=("exactMatch","closeMatch","broadMatch","relatedMatch","narrowMatch",
           "broader","narrower","related","inScheme")
DCT_REFS=("isReplacedBy","replaces","source","spatial")
OFFICIAL_SOURCES={
    "insee_2026":"https://www.insee.fr/fr/metadonnees/geographie/commune/05001-abries-ristolas",
    "insee_commune_deleguee":"https://www.insee.fr/fr/metadonnees/geographie/commune-deleguee/05001-abries",
    "arrete_creation_2018":"https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000038316958",
}
def texts(el,namespace,tag):
    return [{"value":(x.text or "").strip(),"lang":x.get(XML+"lang"),
             "datatype":x.get(RDF+"datatype")}
            for x in el.findall(namespace+tag) if (x.text or "").strip()]

def uris(el,ns,tag):
    return sorted({x.get(RDF+"resource") or (x.text or "").strip()
                   for x in el.findall(ns+tag)
                   if x.get(RDF+"resource") or (x.text or "").strip()})

def fragment(el,ark):
    props={
        "ark_pactols":ark,
        "rdf_type":uris(el,RDF,"type"),
        "skos_literals":{key:texts(el,SKOS,key) for key in SKOS_ELEMENTS},
        "skos_relations":{key:uris(el,SKOS,key) for key in SKOS_REFS},
        "dct_relations":{key:uris(el,DCT,key) for key in DCT_REFS},
        "deprecated":any((x.text or "").strip().lower() in ("true","1")
                          for x in el.findall(OWL+"deprecated")),
        "owl_sameAs":uris(el,OWL,"sameAs"),
    }
    props["exactMatch_INSEE"]=[uri for uri in props["skos_relations"]["exactMatch"]
                              if uri.lower().startswith(("http://id.insee.fr/geo/","https://id.insee.fr/geo/"))]
    return props

def audit_cog(cog:dict,published:dict):
    if (cog.get("region")!="paca" or cog.get("millesime_cog")!=2026
        or len(cog.get("periodes_com",[]))!=1116
        or len(cog.get("alignements_Pactols_COG_valides_2026",[]))!=103):
        raise ValueError("Chronologie PACA altérée")
    if (published.get("schema")!="adlfi.lieux.pactols.paca.sept_communes_nouvelles.2026.public.v1"
        or published.get("alignements_total_PACA_2026")!=945
        or published.get("exceptions_restantes")!=["05001"]):
        raise ValueError("La couverture PACA précédente n'est pas celle de référence")
    periods=sorted((x for x in cog["periodes_com"]
                    if x["code_insee"]==COG and x["typecom"]=="COM"),
                   key=lambda x:x["debut_inclus"])
    if (len(periods)!=2 or periods[0]["libelle"]!=OLD_LABEL
        or periods[0]["fin_exclue"]!="2019-01-01"
        or periods[1]["libelle"]!=NEW_LABEL
        or periods[1]["debut_inclus"]!="2019-01-01"
        or periods[1]["fin_exclue"] is not None):
        raise ValueError("Historique Abriès/Abriès-Ristolas modifié")
    events=[{k:e[k] for k in
             ("mod","code_avant","code_apres","date_effet","libelle_avant","libelle_apres",
              "typecom_avant","typecom_apres","id")}
            for e in cog["lignes_mouvements_cog"]
            if e["mod"]=="32" and e["code_apres"]==COG
            and e["date_effet"]=="2019-01-01"]
    if not any(e["code_avant"]=="05001" and e["libelle_avant"]=="Abriès"
               and e["libelle_apres"]=="Abriès-Ristolas" and e["typecom_apres"]=="COM"
               for e in events):
        raise ValueError("Fusion Abriès non établie")
    if not any(e["code_avant"]=="05120" and e["libelle_avant"]=="Ristolas"
               and e["libelle_apres"]=="Abriès-Ristolas" for e in events):
        raise ValueError("Fusion Ristolas non établie")
    return {"nom_COG_2026":NEW_LABEL,"code_COG_2026":COG,
            "debut_identite_commune_nouvelle":"2019-01-01",
            "ancienne_commune_code_conserve":OLD_LABEL,
            "ancienne_commune_rapprochee":"Ristolas",
            "evenements_MOD32":events,"sources_officielles":OFFICIAL_SOURCES}

def audit_rdf(rdf:Path):
    if sha256(rdf)!=RDF_SHA:
        raise ValueError("Empreinte RDF Pactols différente du snapshot validé")
    recorded={}
    all_names=Counter()
    count=0
    parser=ET.iterparse(rdf,events=("start","end"))
    _,root=next(parser)
    if root.tag!=RDF+"RDF":raise ValueError("Document RDF invalide")
    for ev,el in parser:
        if ev!="end" or el.tag not in (SKOS+"Concept",RDF+"Description"):
            continue
        m=ARK.fullmatch(el.get(RDF+"about",""))
        if not m:
            el.clear();root.clear();continue
        ark=m.group(1)
        if el.tag==RDF+"Description" and not any(
            x.get(RDF+"resource")=="http://www.w3.org/2004/02/skos/core#Concept"
            for x in el.findall(RDF+"type")):
            el.clear();root.clear();continue
        count+=1
        pre=[x.text.strip() for x in el.findall(SKOS+"prefLabel")
             if x.text and (x.get(XML+"lang") or "").lower().startswith("fr")]
        alt=[x.text.strip() for x in el.findall(SKOS+"altLabel")
             if x.text and (x.get(XML+"lang") or "").lower().startswith("fr")]
        matches=[n for n in (*pre,*alt) if norm(n) in (norm(OLD_LABEL),norm(NEW_LABEL),norm(OTHER))]
        for n in pre:
            if norm(n)==norm(NEW_LABEL):
                all_names[ark]+=1
        if ark in (OLD,NEW) or matches:
            if ark in recorded:raise ValueError("Concept RDF répété : "+ark)
            frag=fragment(el,ark)
            frag["motifs_reperage_lexical"]=sorted(set(matches))
            recorded[ark]=frag
        el.clear();root.clear()
    if count!=EXPECTED_COUNT:
        raise ValueError("Nombre de concepts RDF inattendu : "+str(count))
    if OLD not in recorded or NEW not in recorded or len(all_names)!=1 or NEW not in all_names:
        raise ValueError("Concept Pactols contemporain non unique ou absent")
    old=recorded[OLD]
    new=recorded[NEW]
    old_pref=[x["value"] for x in old["skos_literals"]["prefLabel"] if x["lang"]=="fr"]
    new_pref=[x["value"] for x in new["skos_literals"]["prefLabel"] if x["lang"]=="fr"]
    if old_pref!=[OLD_LABEL] or new_pref!=[NEW_LABEL]:
        raise ValueError("Libellés Pactols des deux concepts divergents")
    if (old["exactMatch_INSEE"]!=["http://id.insee.fr/geo/commune/05001"]
        or new["exactMatch_INSEE"]):
        raise ValueError("Présence d'un alignement Insee sur un concept inattendu")
    if new["deprecated"] or new["dct_relations"]["isReplacedBy"]:
        raise ValueError("Concept Pactols contemporain déprécié ou remplacé")
    return {"concepts_RDF_examines":count,
            "nombre_concepts_prefLabel_fr_Abriès_Ristolas":len(all_names),
            "concept_actuel":new,
            "concept_ancienne_commune":old,
            "autres_concepts_lexicaux":[v for k,v in sorted(recorded.items()) if k not in (OLD,NEW)],
            "alignement_INSEE_du_concept_actuel":"AUCUN",
            "concordance_liberte_ARK":"NE_PAS_CONFONDRE_LES_IDENTITES"}

def construire(rdf,cog,published):
    proof=audit_rdf(rdf)
    administrative=audit_cog(cog,published)
    new=proof["concept_actuel"]
    old=proof["concept_ancienne_commune"]
    return {
        "schema":SCHEMA,
        "statut":"RECETTE_NON_VALIDANTE",
        "sources":{
            "pactols_RDF":{"commit":RDF_COMMIT,"sha256":RDF_SHA},
            "COG":{"fichier":"docs/data/lieux-chronologie/cog-paca.json","millesime":"2026-01-01"},
            "publication_preexistante":"docs/data/lieux-chronologie/pactols-paca-communes-nouvelles-2026.json",
        },
        "administratif":administrative,
        "rdf":proof,
        "bilan":{
            "concepts_RDF_examines":proof["concepts_RDF_examines"],
            "prefLabel_actuel_unique":True,
            "ancienne_commune_ARK_distincte":old["ark_pactols"]!=new["ark_pactols"],
            "exactMatch_INSEE_nouveau":len(new["exactMatch_INSEE"]),
            "nouveaux_ARK_valides":0,
            "communes_PACA_alignees_avant":945,
            "geometries_ajoutees":0,
            "relations_historiques_inferees":0,
        },
        "decision":"À instruire : l'unicité lexicale et la légalité COG ne suffisent pas, seules, à établir une identité Pactols–COG.",
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ("rdf","cog","publie","sortie"):
        p.add_argument("--"+arg,required=True,type=Path)
    args=p.parse_args()
    if args.sortie.exists() or "docs" in args.sortie.resolve().parts:
        raise ValueError("Rapport neuf en recette uniquement")
    report=construire(
        args.rdf,
        json.loads(args.cog.read_text(encoding="utf-8")),
        json.loads(args.publie.read_text(encoding="utf-8")))
    args.sortie.parent.mkdir(parents=True,exist_ok=True)
    args.sortie.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("PACA_ABRIES_RISTOLAS_RDF_AUDIT",json.dumps({
        "bilan":report["bilan"],
        "nouveau":report["rdf"]["concept_actuel"],
        "ancien":report["rdf"]["concept_ancienne_commune"],
        "sha256":sha256(args.sortie)
    },ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
