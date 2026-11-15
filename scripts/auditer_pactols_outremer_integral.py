#!/usr/bin/env python3
"""Criblage de 233 entités ultramarines COG contre le RDF COMPLET Pactols-Lieux.

Non validant : un exactMatch déclaré dans Pactols n'est pas une validation
éditoriale AdlFI, et une ressemblance lexicale n'est pas un alignement.
Les codes sont des identifiants de zonages typés, NON des preuves de même lieu.
Source RDF officielle Frantiq LFS figée au 22 juillet 2026.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

SHA_PACTOLS = "3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7"
SHA_COMMUNES = "7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3"
SHA_COMER = "d1f08ba101abf50c0a5db5cf7b24a50397bf68706aa658e4027a4fb933f059ed"
SHA_ZONAGES = "9ca82ec1104c9a2307ad368ab40e47afa801137845901ca844bb700dc8d7c9d8"
RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
SKOS = "{http://www.w3.org/2004/02/skos/core#}"
OWL = "{http://www.w3.org/2002/07/owl#}"
LANG = "{http://www.w3.org/XML/1998/namespace}lang"
ARK_RE = re.compile(r"/ark:/26678/([A-Za-z0-9_-]+)(?:$|[?#])")
INSEE_RE = re.compile(r"^https?://id\.insee\.fr/geo/([^/]+)/([^/?#]+)/?$", re.I)
TERRITOIRES_DROM = {"971","972","973","974","976"}
NATURES = {"COM","DIS","CIR","CPT","CDM"}
FIELDS = [
    "cible_id","famille","niveau","nature_zonage","code_cog","code_parent_comer",
    "libelle_cog","libelle_parent","ark_candidat","pref_fr","alt_fr","hidden_fr",
    "liens_insee_mentionnes","uri_pactols","signaux",
    "correspondance_code_insee_meme_valeur","deprecie","atteste_XML_AdlFI",
    "decision_editoriale","note_instruction",
]

def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1 << 20),b""):
            h.update(chunk)
    return h.hexdigest()

def norm(s):
    s=str(s or "").replace("œ","oe").replace("Œ","Oe")
    s=unicodedata.normalize("NFKD",s).casefold()
    s="".join(c for c in s if unicodedata.category(c)!="Mn")
    return " ".join(re.sub(r"[^a-z0-9]+"," ",s).split())

def lire(path,required):
    with Path(path).open("r",encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f,delimiter=",")
        if not set(required).issubset(reader.fieldnames or ()):
            raise ValueError("Colonnes COG absentes : "+str(path))
        return list(reader)

def preparer_cibles(communes,comer,zonages):
    cibles=[]
    for r in communes:
        if r["TYPECOM"]=="COM" and r["DEP"] in TERRITOIRES_DROM:
            cibles.append({
                "cible_id":"DROM:COM:"+r["COM"], "famille":"DROM",
                "niveau":"commune", "nature_zonage":"COM",
                "code_cog":r["COM"], "code_parent_comer":"",
                "libelle_cog":r["LIBELLE"],"libelle_parent":r["DEP"],
                "formes":[r["LIBELLE"],r.get("NCCENR","")],
            })
    parents={r["COMER"]:r["LIBELLE"] for r in comer}
    for r in comer:
        cibles.append({
            "cible_id":"COMER:TERRITOIRE:"+r["COMER"],"famille":"COMER",
            "niveau":"collectivite_ou_territoire","nature_zonage":"TERRITOIRE",
            "code_cog":r["COMER"],"code_parent_comer":"",
            "libelle_cog":r["LIBELLE"],"libelle_parent":"",
            "formes":[r["LIBELLE"],r.get("NCCENR","")],
        })
    for r in zonages:
        nature=r["NATURE_ZONAGE"]
        if nature not in NATURES or r["COMER"] not in parents:
            raise ValueError("Zonage COMER sans nature/parent attesté : "+repr(r))
        cibles.append({
            "cible_id":"COMER:"+nature+":"+r["COM_COMER"],"famille":"COMER",
            "niveau":"subdivision","nature_zonage":nature,
            "code_cog":r["COM_COMER"],"code_parent_comer":r["COMER"],
            "libelle_cog":r["LIBELLE"],"libelle_parent":parents[r["COMER"]],
            "formes":[r["LIBELLE"],r.get("NCCENR","")],
        })
    ids=[r["cible_id"] for r in cibles]
    if len(set(ids))!=len(ids):
        raise ValueError("Identifiants de cibles dupliqués")
    cibles.sort(key=lambda r:r["cible_id"])
    return cibles

def apercu_concept(el):
    uri=el.get(RDF+"about","")
    m=ARK_RE.search(uri)
    if not m:return None
    labels={"pref":[],"alt":[],"hidden":[]}
    exact=[];deprecated=False
    for child in el:
        if child.tag in (SKOS+"prefLabel",SKOS+"altLabel",SKOS+"hiddenLabel"):
            lang=child.get(LANG,"").lower()
            if lang=="fr" or lang.startswith("fr-"):
                val="".join(child.itertext()).strip()
                if val:
                    key={SKOS+"prefLabel":"pref",SKOS+"altLabel":"alt",
                         SKOS+"hiddenLabel":"hidden"}[child.tag]
                    labels[key].append(val)
        elif child.tag==SKOS+"exactMatch":
            u=child.get(RDF+"resource") or "".join(child.itertext()).strip()
            if u:exact.append(u)
        elif child.tag==OWL+"deprecated":
            deprecated="".join(child.itertext()).strip().lower() in ("true","1")
    return {
        "ark":"26678/"+m.group(1),"uri":uri,
        **{k:sorted(set(v)) for k,v in labels.items()},
        "exact":sorted(set(exact)),"deprecie":deprecated,
    }

def scanner_rdf(path,cibles,xml_arks=None,min_concepts=30000):
    # Index inverse des libellés, pour éviter 233 comparaisons/concept.
    by_label=collections.defaultdict(set)
    by_code=collections.defaultdict(set)
    cibles_by_id={r["cible_id"]:r for r in cibles}
    for r in cibles:
        for val in r["formes"]:
            if norm(val):by_label[norm(val)].add(r["cible_id"])
        by_code[r["code_cog"]].add(r["cible_id"])
    found=collections.defaultdict(dict)
    nconcept=0
    root=None;depth=0
    for event,elem in ET.iterparse(path,events=("start","end")):
        if event=="start":
            depth+=1
            if depth==1:
                root=elem
                if elem.tag!=RDF+"RDF":
                    raise ValueError("Le fichier n'est pas RDF/XML")
            continue
        if depth==2:
            if elem.tag in (SKOS+"Concept",RDF+"Description"):
                c=apercu_concept(elem)
                if c:
                    nconcept+=1
                    evidences=collections.defaultdict(set)
                    for kind in ("pref","alt","hidden"):
                        for lab in c[kind]:
                            key=norm(lab)
                            for id in by_label.get(key,()):
                                evidences[id].add(kind+"_fr_exact")
                            # Qualificatif entre parenthèses : indice lexical,
                            # PAS preuve que le qualificatif désigne le bon territoire.
                            stripped=re.sub(r"\s*\([^()]{2,100}\)\s*$","",lab)
                            if stripped!=lab:
                                for id in by_label.get(norm(stripped),()):
                                    evidences[id].add(kind+"_fr_qualifie")
                    for u in c["exact"]:
                        m=INSEE_RE.match(u)
                        if m:
                            code=m.group(2)
                            for id in by_code.get(code,()):
                                evidences[id].add("lien_insee_code_meme_valeur")
                    for id,signaux in evidences.items():
                        if c["ark"] in found[id]:
                            raise ValueError("ARK dupliqué au sein d'une cible : "+c["ark"])
                        row=cibles_by_id[id]
                        matched_urls=[u for u in c["exact"] if
                            (m:=INSEE_RE.match(u)) and m.group(2)==row["code_cog"]]
                        found[id][c["ark"]]={
                            **{k:row[k] for k in (
                                "cible_id","famille","niveau","nature_zonage",
                                "code_cog","code_parent_comer","libelle_cog","libelle_parent")},
                            "ark_candidat":c["ark"],
                            "pref_fr":json.dumps(c["pref"],ensure_ascii=False),
                            "alt_fr":json.dumps(c["alt"],ensure_ascii=False),
                            "hidden_fr":json.dumps(c["hidden"],ensure_ascii=False),
                            "liens_insee_mentionnes":json.dumps(matched_urls,ensure_ascii=False),
                            "uri_pactols":c["uri"],
                            "signaux":"|".join(sorted(signaux)),
                            "correspondance_code_insee_meme_valeur":"oui" if matched_urls else "non",
                            "deprecie":"oui" if c["deprecie"] else "non",
                            "atteste_XML_AdlFI":("oui" if c["ark"] in xml_arks else "non")
                                   if xml_arks is not None else "non_verifie",
                            "decision_editoriale":"NON_VALIDE_A_INSTRUIRE",
                            "note_instruction":"Égalité de code/forme non suffisante, vérifier portée spatiale, temps et type d'entité",
                        }
            elem.clear()
            if root is not None:root.clear()
        depth-=1
    if nconcept<min_concepts:
        raise ValueError("RDF intégral non reconnu : "+str(nconcept)+" concepts")
    return nconcept,found

def ecrire_csv(path,rows,fields):
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.DictWriter(f,delimiter=";",fieldnames=fields,extrasaction="ignore")
        writer.writeheader();writer.writerows(rows)

def produire(rdf,communes,comer,zonages,sortie,xml=None,controle_sha=True):
    sources={"rdf":Path(rdf),"communes":Path(communes),
             "comer":Path(comer),"zonages":Path(zonages)}
    expected={"rdf":SHA_PACTOLS,"communes":SHA_COMMUNES,
              "comer":SHA_COMER,"zonages":SHA_ZONAGES}
    for role,path in sources.items():
        if controle_sha and digest(path)!=expected[role]:
            raise ValueError("Source différente du snapshot vérifié : "+role)
    cibles=preparer_cibles(
        lire(communes,{"TYPECOM","DEP","COM","LIBELLE","NCCENR"}),
        lire(comer,{"COMER","LIBELLE","NCCENR"}),
        lire(zonages,{"COM_COMER","COMER","NATURE_ZONAGE","LIBELLE","NCCENR"}),
    )
    if controle_sha and (len(cibles),collections.Counter(x["famille"] for x in cibles))!=(
            233,{"DROM":129,"COMER":104}):
        raise ValueError("Effectifs de cibles inattendus (129+95+9)")
    xml_arks=None
    if xml:
        doc=json.loads(Path(xml).read_text(encoding="utf-8"))
        if doc.get("unite")!="concept_pactols_atteste_dans_XML":
            raise ValueError("Index XML AdlFI incompatible")
        xml_arks={r["ark_pactols"] for r in doc["autorites"]}
        if controle_sha and len(xml_arks)!=9928:
            raise ValueError("Le corpus XML devrait comporter 9 928 ARK")
    nb,found=scanner_rdf(rdf,cibles,xml_arks)
    candidates=[r for id in sorted(found) for ark,r in sorted(found[id].items())]
    synth=[]
    for t in cibles:
        rows=list(found[t["cible_id"]].values())
        names=[r["ark_candidat"] for r in rows if any(
            k in r["signaux"] for k in ("pref_fr_exact","alt_fr_exact"))]
        by_code=[r["ark_candidat"] for r in rows
                 if r["correspondance_code_insee_meme_valeur"]=="oui"]
        synth.append({
            **{k:t[k] for k in ("cible_id","famille","niveau","nature_zonage",
                               "code_cog","code_parent_comer","libelle_cog","libelle_parent")},
            "nb_candidats":len(rows),"nb_signaux_nom_exact":len(names),
            "nb_liens_insee_code_egal":len(by_code),
            "nb_candidats_attestes_xml":sum(x["atteste_XML_AdlFI"]=="oui" for x in rows),
            "qualif":("aucun_candidat_snapshot" if not rows
                      else "plusieurs_candidats_a_desambiguiser" if len(rows)>1
                      else "candidat_unique_non_valide"),
            "validation_editoriale":"A_FAIRE",
        })
    sortie=Path(sortie)
    if "docs" in sortie.resolve().parts:
        raise ValueError("Aucun résultat de recette dans docs/")
    if sortie.resolve()==Path(rdf).resolve().parent:
        raise ValueError("Ne pas écrire à côté de la source RDF")
    sortie.mkdir(parents=True,exist_ok=True)
    ecrire_csv(sortie/"cibles_COG_ultramarin_233.csv",[
        {k:v for k,v in t.items() if k!="formes"} for t in cibles],
        ["cible_id","famille","niveau","nature_zonage","code_cog",
         "code_parent_comer","libelle_cog","libelle_parent"])
    ecrire_csv(sortie/"candidats_Pactols_integral.csv",candidates,FIELDS)
    fields=list(synth[0])
    ecrire_csv(sortie/"synthese_cibles.csv",synth,fields)
    report={
        "schema":"adlfi.lieux.outremer.pactols.integral.audit.v1",
        "statut":"RECETTE_NON_VALIDANTE_NON_PUBLIEE",
        "snapshot_pactols":"2026-07-22",
        "sha256_sources":{role:digest(path) for role,path in sources.items()},
        "source_xml_attestations":(
           {"sha256":digest(xml),"ark":len(xml_arks)} if xml else None),
        "concepts_pactols_parcourus":nb,
        "cibles_cog":len(cibles),
        "cibles_drom":sum(t["famille"]=="DROM" for t in cibles),
        "cibles_comer":sum(t["famille"]=="COMER" for t in cibles),
        "candidatures":len(candidates),
        "cibles_avec_candidats":sum(r["nb_candidats"]>0 for r in synth),
        "cibles_avec_plusieurs_candidats":sum(r["nb_candidats"]>1 for r in synth),
        "cibles_sans_candidat":[r["cible_id"] for r in synth if not r["nb_candidats"]],
        "types_evidence":dict(sorted(collections.Counter(
            signal for row in candidates for signal in row["signaux"].split("|")
            if signal).items())),
        "nouveaux_alignements_valides":0,
        "geometries_historiques_attribuees":0,
        "precautions":[
           "Le RDF est un snapshot daté : l'absence de signal ne prouve pas l'absence d'ARK vivant.",
           "Le résultat COG se rapporte à des codes typés (COM, DIS, CIR, CPT, CDM, TERRITOIRE).",
           "Un skos:exactMatch existant dans Pactols n'est pas une validation éditoriale AdlFI.",
           "Plusieurs concepts peuvent porter un nom homonyme ou un code réutilisé.",
           "Une égalité de libellé n'est pas une relation administrative ou historique.",
           "Les données XML AdlFI (si fournies) sont des attestations, non une vue intégrale du thésaurus.",
        ],
    }
    (sortie/"rapport_pactols_outremer_integral.json").write_text(
        json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("rdf","communes","comer","zonages","sortie"):
        p.add_argument("--"+name,required=True,type=Path)
    p.add_argument("--xml",type=Path)
    args=p.parse_args()
    report=produire(**vars(args))
    print(json.dumps({k:report[k] for k in (
       "concepts_pactols_parcourus","cibles_cog","candidatures",
       "cibles_avec_candidats","cibles_avec_plusieurs_candidats",
       "types_evidence")},ensure_ascii=False,indent=2))
