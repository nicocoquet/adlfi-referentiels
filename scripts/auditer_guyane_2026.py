#!/usr/bin/env python3
"""Lot Guyane : instruction documentaire COG 1943-2026, Pactols et géométries.

Ce script ne valide aucun alignement, n'infère aucune succession, ne génère
aucun polygone et ne modifie jamais le site docs/.
"""
from __future__ import annotations

import argparse
import collections
import csv
import gzip
import hashlib
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

COG_SHAS = {
    "v_commune_2026.csv": "7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3",
    "v_commune_depuis_1943.csv": "08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee",
    "v_mvt_commune_2026.csv": "8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1",
}
PACS = {
    "repository": "frantiq/PACTOLS",
    "commit": "69bf9697e24cefd645a69465bbd271702786285a",
    "relative_path": "pactols-latest-version/pactols_lieux_all/Pactols_Lieux_th17_20260722.rdf",
    "sha256": "3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7",
}
GEOM_SHA = "4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778"
RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
SKOS = "{http://www.w3.org/2004/02/skos/core#}"
OWL = "{http://www.w3.org/2002/07/owl#}"
XML = "{http://www.w3.org/XML/1998/namespace}"
INSEE_URI = re.compile(r"^https?://id[.]insee[.]fr/geo/commune/(973[0-9]{2})/?$")
ARK = re.compile(r"^https?://ark[.]frantiq[.]fr/ark:/((?:26678)/[A-Za-z0-9]+)$")
SCHEMA = "adlfi.lieux.guyane.audit.cog-pactols-geom.v1"


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def csv_lire(path: Path, colonnes: set[str]) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader=csv.DictReader(f)
        if not colonnes.issubset(reader.fieldnames or []):
            raise ValueError("Colonnes COG absentes : "+str(path))
        rows=list(reader)
    if not rows or any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError("CSV COG incomplet : "+str(path))
    return rows


def normaliser(v: object) -> str:
    text=unicodedata.normalize("NFKD", str(v or "").casefold())
    text="".join(x for x in text if not unicodedata.combining(x))
    return " ".join(re.findall(r"[a-z0-9]+",text))


def lire_reference(path: Path) -> dict:
    data=json.loads(path.read_text(encoding="utf8"))
    if data.get("schema")!="adlfi.lieux.recherche.outremer.public.v1":
        raise ValueError("Index public ultramarin incompatible")
    communes=[]
    for ligne in data["communes"]["973"].splitlines():
        code,libelle=ligne.split("|",1)
        communes.append((code,libelle))
    if len(communes)!=22 or len({c for c,_ in communes})!=22:
        raise ValueError("22 communes Guyane attendues dans la recherche publique")
    return dict(communes)


def lire_pactols(path: Path, communes: dict) -> tuple[dict,dict]:
    """Lire en streaming tous les concepts, sans alignement par simple homonymie.

    Deux types de preuves sont conservés DISTINCTS : URI Insee explicitement
    citée dans un concept, et simple concordance de libellé français.
    """
    codes=set(communes)
    noms=collections.defaultdict(list)
    for code,name in communes.items():
        noms[normaliser(name)].append(code)
    result={c:{"uri_insee_citees":[],"candidatures_lexicales":[]} for c in codes}
    meta={"concepts_examines":0,"concepts_avec_code_insee_guyane":0,
          "liens_insee_rejetes_hors_communes_2026":0}
    ctx=ET.iterparse(path,events=("start","end"))
    _,root=next(ctx)
    if root.tag!=RDF+"RDF":
        raise ValueError("Export Pactols non reconnu comme RDF/XML")
    for event,element in ctx:
        if event!="end" or element.tag not in (SKOS+"Concept",RDF+"Description"):
            continue
        resource=element.get(RDF+"about") or ""
        match=ARK.fullmatch(resource)
        if not match:
            element.clear()
            root.clear()
            continue
        types={x.get(RDF+"resource") for x in element.findall(RDF+"type")}
        if element.tag!=SKOS+"Concept" and (SKOS[1:-1]+"Concept") not in types:
            element.clear()
            root.clear()
            continue
        meta["concepts_examines"]+=1
        labels=[]
        for child in element:
            if child.tag in (SKOS+"prefLabel",SKOS+"altLabel") and child.text \
               and child.get(XML+"lang","").lower().startswith("fr"):
                labels.append({"libelle":child.text.strip(),
                               "propriete":"prefLabel" if child.tag==SKOS+"prefLabel" else "altLabel"})
        cited=set()
        for child in element:
            if child.tag not in (SKOS+"exactMatch",SKOS+"closeMatch",
                                 SKOS+"relatedMatch",OWL+"sameAs"):
                continue
            uri=child.get(RDF+"resource","")
            cm=INSEE_URI.fullmatch(uri)
            if cm:
                cited.add((cm.group(1),child.tag.split("}")[-1],uri))
        if cited:meta["concepts_avec_code_insee_guyane"]+=1
        info={"ark":match.group(1),"source_uri":resource,
              "libelles_fr":labels}
        for code,pred,uri in sorted(cited):
            if code not in codes:
                meta["liens_insee_rejetes_hors_communes_2026"]+=1
                continue
            result[code]["uri_insee_citees"].append({
                **info,"predicat":pred,"uri_insee":uri,
                "statut":"LIEN_SOURCE_NON_VALIDE_PAR_EDITORIAL"})
        terms=collections.defaultdict(list)
        for label in labels:
            for code in noms.get(normaliser(label["libelle"]),[]):
                terms[code].append(label)
        for code,matched_labels in sorted(terms.items()):
            result[code]["candidatures_lexicales"].append({
                **info,"labels_concordants":matched_labels,
                "statut":"HOMONYMIE_CANDIDATE_SANS_PREUVE_IDENTITE"})
        element.clear()
        root.clear()
    for c in result:
        for key in ("uri_insee_citees","candidatures_lexicales"):
            result[c][key].sort(key=lambda o:(o["ark"],o.get("predicat","")))
    return result,meta


def extraire_histoire(courant: list[dict],periodes: list[dict],mouvements: list[dict],
                     communes: dict) -> tuple[dict,list,list]:
    actuel={r["COM"]:r for r in courant if r["TYPECOM"]=="COM" and r["DEP"]=="973"}
    if set(actuel)!=set(communes) or any(
        r["LIBELLE"]!=communes[code] or r["REG"]!="03"
        for code,r in actuel.items()
    ):
        raise ValueError("Liste COG Guyane 2026 non conforme à l'index publié")
    percode=collections.defaultdict(list)
    historique=[]
    for r in periodes:
        if r["TYPECOM"]!="COM" or not r["COM"].startswith("973"):continue
        begin,end=r["DATE_DEBUT"],r["DATE_FIN"] or None
        if not begin or (end and end<begin):
            raise ValueError("Épisode COG Guyane incohérent : "+r["COM"])
        date.fromisoformat(begin)
        if end:date.fromisoformat(end)
        row={"code":r["COM"],"libelle":r["LIBELLE"],
             "debut_inclus":begin,"fin_exclue":end,
             "fichier_source":"v_commune_depuis_1943.csv",
             "identite_juridique_retroactive":"NON_ETABLIE",
             "geometrie_historique":None}
        percode[r["COM"]].append(row)
        historique.append(row)
    for code in percode:
        periods=sorted(percode[code],key=lambda x:x["debut_inclus"])
        for i,p in enumerate(periods[1:],1):
            previous=periods[i-1]
            if previous["fin_exclue"] is None or previous["fin_exclue"]>p["debut_inclus"]:
                raise ValueError("Épisodes du même code en conflit : "+code)
    active=[
        x for x in historique
        if x["debut_inclus"]<="2026-01-01" and
           (x["fin_exclue"] is None or "2026-01-01"<x["fin_exclue"])
    ]
    if len(active)!=22 or {x["code"] for x in active}!=set(communes):
        raise ValueError("L'état historique COG actif diffère du COG courant 2026")
    events=[]
    for r in mouvements:
        prev,next_=r["COM_AV"],r["COM_AP"]
        if not prev.startswith("973") and not next_.startswith("973"):continue
        row={k:r[k] for k in ("MOD","DATE_EFF","TYPECOM_AV","COM_AV","LIBELLE_AV",
                               "TYPECOM_AP","COM_AP","LIBELLE_AP")}
        events.append(row)
    events.sort(key=lambda x:(x["DATE_EFF"],x["COM_AV"],x["COM_AP"],
                              x["MOD"],x["LIBELLE_AV"],x["LIBELLE_AP"]))
    for event in events:
        date.fromisoformat(event["DATE_EFF"])
    return percode, sorted(historique,key=lambda x:(x["code"],x["debut_inclus"])),events


def qualifier_geometries(path: Path, communes: dict) -> dict:
    try:
        from shapely.geometry import shape
        from shapely.validation import explain_validity
        from shapely.ops import transform
        from pyproj import Transformer
    except ImportError as e:
        raise RuntimeError("Shapely et pyproj requis pour l'audit géométrique") from e
    opener=gzip.open if path.suffix==".gz" else open
    with opener(path,"rt",encoding="utf8") as f:
        collection=json.load(f)
    if collection.get("type")!="FeatureCollection":
        raise ValueError("Contours géographiques incompatibles")
    bycode=collections.defaultdict(list)
    for feat in collection.get("features",[]):
        code=str(feat.get("properties",{}).get("code",""))
        if code in communes:bycode[code].append(feat)
    projector=Transformer.from_crs("EPSG:4326","EPSG:6933",always_xy=True)
    results={}
    for code in sorted(communes):
        feats=bycode[code]
        if len(feats)!=1:
            results[code]={"statut":"ABSENTE_OU_DUPLIQUEE","nombre_features":len(feats),
                           "contour_adopte":False,"geometrie_historique":None}
            continue
        geom=shape(feats[0].get("geometry"))
        good=geom.is_valid and not geom.is_empty and geom.geom_type in ("Polygon","MultiPolygon")
        bounds=geom.bounds
        if len(bounds)!=4 or not (-60<=bounds[0]<=bounds[2]<=-48 and
            0<=bounds[1]<=bounds[3]<=7):
            raise ValueError("Géométrie de commune guyanaise hors domaine : "+code)
        area=round(transform(projector.transform,geom).area/1e6,3) if good else None
        results[code]={"statut":"PRESENTE_VALIDE_A_QUALIFIER" if good else "INVALIDITE_A_INSTRUIRE",
                       "type":geom.geom_type,
                       "validite_topologique":bool(geom.is_valid),
                       "motif_invalidite":"" if geom.is_valid else explain_validity(geom),
                       "surface_approximative_km2_egal_aire":area,
                       "bbox_wgs84":[round(v,6) for v in bounds],
                       "edition_source":"2026-05-04",
                       "contour_adopte":False,
                       "geometrie_historique":None}
    return results


def generer(communes: dict, percode: dict, hist: list, events: list,
            geometries: dict, pactols: dict, pactols_meta: dict) -> dict:
    suivi=[]
    for code,name in sorted(communes.items()):
        ev=[e for e in events if code in (e["COM_AV"],e["COM_AP"])]
        concepts=pactols[code]
        suivi.append({
            "code_COG_2026":code,"libelle_COG_2026":name,
            "uri_insee":"http://id.insee.fr/geo/commune/"+code,
            "type":"commune","region_COG_2026":"03","departement_COG_2026":"973",
            "historique_meme_code":percode.get(code,[]),
            "evenements_avec_code_2026":ev,
            "statut_alignement_Pactols":"A_INSTRUIRE",
            "pactols_uri_insee_source":concepts["uri_insee_citees"],
            "pactols_concordances_lexicales":concepts["candidatures_lexicales"],
            "geometrie_2026":geometries[code],
            "continuites_avec_autres_codes":"NON_INSTRUITES",
        })
    return {
        "schema":SCHEMA,"statut":"RECETTE_NON_PUBLIEE",
        "source_COG":"Insee COG au 1er janvier 2026, historique depuis 1943",
        "source_Pactols":"export RDF Lieux 22 juillet 2026 épinglé",
        "date_contours":"2026-05-04",
        "communes":suivi,
        "historique_codes_973":hist,
        "mouvements_source_avec_code_973":events,
        "bilan":{
            "communes_COG_2026":len(suivi),
            "codes_distincts_historiques_973":len(percode),
            "periodes_historiques_973":len(hist),
            "mouvements_impliquant_code_973":len(events),
            "geometries_topologiquement_valides":sum(
                x["geometrie_2026"]["statut"]=="PRESENTE_VALIDE_A_QUALIFIER"
                for x in suivi),
            "candidatures_avec_uri_source":sum(
                bool(x["pactols_uri_insee_source"]) for x in suivi),
            "communes_avec_concordance_lexicale":sum(
                bool(x["pactols_concordances_lexicales"]) for x in suivi),
            "correspondances_Pactols_validees_par_cet_audit":0,
            "contours_adoptes_par_cet_audit":0,
            "relations_de_succession_creees":0,
            "source_Pactols_stats":pactols_meta,
        },
        "avertissements":[
            "COG historique : une continuité de code ou de nom ne prouve pas une identité juridique intemporelle.",
            "Mouvements : événements officiels, pas une succession automatiquement validée.",
            "Un skos:exactMatch ou owl:sameAs dans Pactols est une assertion source, non une décision AdlFI.",
            "Une correspondance de libellés peut être une homonymie.",
            "Le millésime 2026 des contours ne peut jamais être rétroprojeté aux situations anciennes.",
            "Les surfaces projetées en EPSG:6933 sont des diagnostics, pas des surfaces juridiques.",
            "Aucun ARK ni aucune géométrie ne sont ajoutés dans docs/.",
        ],
    }


def produire(cog_dir: Path,pactols_rdf: Path,geojson: Path,
            public_index: Path,sortie: Path,strict: bool=True) -> dict:
    for path in (pactols_rdf,geojson,public_index):
        if not path.is_file():raise FileNotFoundError(path)
    if "docs" in sortie.resolve().parts or sortie.resolve().is_relative_to(cog_dir.resolve()):
        raise ValueError("La sortie doit rester une recette hors docs/ et hors sources")
    if strict:
        for name,expected in COG_SHAS.items():
            if sha256(cog_dir/name)!=expected:
                raise ValueError("Empreinte source COG 2026 non conforme : "+name)
        if sha256(pactols_rdf)!=PACS["sha256"]:
            raise ValueError("Export Pactols Lieux différent du commit épinglé")
        if sha256(geojson)!=GEOM_SHA:
            raise ValueError("Contours 2026 différents de la recette précédente")
    communes=lire_reference(public_index)
    courant=csv_lire(cog_dir/"v_commune_2026.csv",{"COM","LIBELLE","TYPECOM","DEP","REG"})
    periodes=csv_lire(cog_dir/"v_commune_depuis_1943.csv",
                     {"COM","LIBELLE","TYPECOM","DATE_DEBUT","DATE_FIN"})
    mouvements=csv_lire(cog_dir/"v_mvt_commune_2026.csv",
                       {"MOD","DATE_EFF","COM_AV","COM_AP","TYPECOM_AV","TYPECOM_AP",
                        "LIBELLE_AV","LIBELLE_AP"})
    parcode,hist,events=extraire_histoire(courant,periodes,mouvements,communes)
    geom=qualifier_geometries(geojson,communes)
    concepts,stats=lire_pactols(pactols_rdf,communes)
    rapport=generer(communes,parcode,hist,events,geom,concepts,stats)
    if strict and (rapport["bilan"]["communes_COG_2026"]!=22 or
                   rapport["bilan"]["geometries_topologiquement_valides"]!=22):
        raise ValueError("Audit Guyane 22 communes ou contours 2026 non conforme")
    sortie.mkdir(parents=True,exist_ok=True)
    resultats={
        "guyane-22-communes-audit.json":rapport,
        "guyane-historique-mouvements.json":{
            "schema":SCHEMA,"statut":"RECETTE_NON_PUBLIEE",
            "periodes":hist,"mouvements":events},
    }
    for name,obj in resultats.items():
        (sortie/name).write_text(json.dumps(obj,ensure_ascii=False,
                        sort_keys=True,indent=2)+"\n",encoding="utf8")
    with (sortie/"guyane-revue-22-communes.csv").open(
        "w",encoding="utf-8-sig",newline="") as f:
        cols=("code_COG_2026","libelle_COG_2026","nb_episodes_meme_code",
              "nb_evenements_courants","nb_uri_insee_Pactols",
              "nb_candidats_lexicaux","statut_alignement_Pactols",
              "statut_geom_2026","surface_diagnostic_km2")
        wr=csv.writer(f,delimiter=";")
        wr.writerow(cols)
        for e in rapport["communes"]:
            wr.writerow((e["code_COG_2026"],e["libelle_COG_2026"],
               len(e["historique_meme_code"]),len(e["evenements_avec_code_2026"]),
               len(e["pactols_uri_insee_source"]),len(e["pactols_concordances_lexicales"]),
               e["statut_alignement_Pactols"],e["geometrie_2026"]["statut"],
               e["geometrie_2026"]["surface_approximative_km2_egal_aire"]))
    manifest={
        "statut":"RECETTE_NON_PUBLIEE","schema":SCHEMA,
        "bilan":rapport["bilan"],
        "sources_sha256":{**{x:sha256(cog_dir/x) for x in COG_SHAS},
                "pactols_lieux_rdf":sha256(pactols_rdf),
                "communes_100m_geojson_gz":sha256(geojson),
                "index_public_outremer_2026":sha256(public_index)},
        "sorties_sha256":{name:sha256(sortie/name) for name in [
            "guyane-22-communes-audit.json",
            "guyane-historique-mouvements.json",
            "guyane-revue-22-communes.csv"]},
        "nouveaux_alignements_Pactols":0,"geometries_publiees":0,
    }
    (sortie/"manifest-guyane.json").write_text(
        json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf8")
    return manifest


if __name__=="__main__":
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--cog-dir",required=True,type=Path)
    a.add_argument("--pactols-rdf",required=True,type=Path)
    a.add_argument("--geojson",required=True,type=Path)
    a.add_argument("--public-index",required=True,type=Path)
    a.add_argument("--sortie",required=True,type=Path)
    x=a.parse_args()
    print(json.dumps(produire(**vars(x)),ensure_ascii=False,sort_keys=True,indent=2))
