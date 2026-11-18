#!/usr/bin/env python3
"""Audit probatoire non validant des 17 ARK PDL au libellé contemporain sans URI INSEE.

Source RDF : snapshot Pactols th17 du 22-07-2026 vérifié par SHA-256.
Source COG : chronologie PDL 2026 déjà versionnée, sans retéléchargement officiel.
"""
from __future__ import annotations

import argparse
import collections
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from auditer_pactols_cog_regions_prioritaires_2026 import sha
from auditer_pactols_polynesie_2026 import RDF, SKOS, OWL, DCT, XML, ARK, RDF_SHA, norm

SCHEMA = "adlfi.lieux.pdl.17-ark-sans-insee.prequalification.2026.v1"
REGISTRE_SCHEMA = "adlfi.lieux.pdl.24-divergences.2026.registre-non-validant.v1"
PUBLICATIONS = (
    "pactols-pdl-2026.json",
    "pactols-pdl-uuid-resolus-2026.json",
    "pactols-pdl-communes-nouvelles-lot01-2026.json",
    "pactols-pdl-chemille-2026.json",
    "pactols-pdl-communes-nouvelles-lot02-2026.json",
    "pactols-pdl-oree-anjou-mod50-2026.json",
)
INSEE_PREFIX = ("http://id.insee.fr/geo/", "https://id.insee.fr/geo/")


def analyser_concepts(rdf: Path, attendus: dict[str, str]) -> tuple[dict, dict]:
    """Relecture complète du RDF et inventaire des homonymes de prefLabel.

    Ne pas réutiliser l'absence de hit de l'audit 24 comme preuve d'unicité :
    les autres concepts du même nom peuvent posséder un exactMatch différent.
    """
    if sha(rdf) != RDF_SHA:
        raise ValueError("Le RDF Pactols ne correspond pas au snapshot th17 épinglé")
    cible = collections.defaultdict(set)
    for code, nom in attendus.items():
        cible[norm(nom)].add(code)
    arks_retenus = {}
    homonymes = collections.defaultdict(list)
    parser = ET.iterparse(rdf, events=("start", "end"))
    _, root = next(parser)
    if root.tag != RDF + "RDF":
        raise ValueError("Le fichier source n'est pas un RDF/XML")
    for event, elem in parser:
        if event != "end" or elem.tag not in (SKOS + "Concept", RDF + "Description"):
            continue
        match = ARK.fullmatch(elem.get(RDF + "about", ""))
        if not match:
            elem.clear()
            root.clear()
            continue
        if elem.tag == RDF + "Description" and not any(
            x.get(RDF + "resource") == "http://www.w3.org/2004/02/skos/core#Concept"
            for x in elem.findall(RDF + "type")
        ):
            elem.clear()
            root.clear()
            continue
        ark = match.group(1)
        def textes(tag):
            return sorted({(x.text or "").strip() for x in elem.findall(tag)
                           if (x.text or "").strip()})
        def resources(tag):
            return sorted({x.get(RDF + "resource") for x in elem.findall(tag)
                           if x.get(RDF + "resource")})
        prefs = sorted({x.text.strip() for x in elem.findall(SKOS + "prefLabel")
                        if x.text and x.get(XML + "lang", "").lower().startswith("fr")})
        alts = sorted({x.text.strip() for x in elem.findall(SKOS + "altLabel")
                       if x.text and x.get(XML + "lang", "").lower().startswith("fr")})
        matched = sorted({code for label in prefs for code in cible.get(norm(label), ())})
        for code in matched:
            homonymes[code].append(ark)
        if ark in attendus.values() or matched:
            if ark in arks_retenus:
                raise ValueError("ARK répété dans le RDF : " + ark)
            exact = resources(SKOS + "exactMatch")
            arks_retenus[ark] = {
                "ark": ark, "prefLabels_fr": prefs, "altLabels_fr": alts,
                "exactMatch": exact,
                "closeMatch": resources(SKOS + "closeMatch"),
                "broader": resources(SKOS + "broader"),
                "related": resources(SKOS + "related"),
                "inScheme": resources(SKOS + "inScheme"),
                "types_RDF": resources(RDF + "type"),
                "historyNote": textes(SKOS + "historyNote"),
                "scopeNote": textes(SKOS + "scopeNote"),
                "definition": textes(SKOS + "definition"),
                "notes": textes(SKOS + "note"),
                "isReplacedBy": resources(DCT + "isReplacedBy"),
                "deprecated": any((x.text or "").strip().lower() in ("true","1")
                                  for x in elem.findall(OWL + "deprecated")),
            }
        elem.clear()
        root.clear()
    return arks_retenus, {code:sorted(set(v)) for code,v in homonymes.items()}


def preparer(registre: dict, cog: dict, publications: list[dict],
             rdf: Path) -> dict:
    if registre.get("schema") != REGISTRE_SCHEMA or registre.get("nombre_dossiers") != 24:
        raise ValueError("Le registre des 24 divergences est absent ou incohérent")
    if cog.get("region") != "pdl" or cog.get("millesime_cog") != 2026:
        raise ValueError("La source COG PDL 2026 est incorrecte")
    published = [a for p in publications for a in p["alignements_Pactols_COG_valides_2026"]]
    codes = {x["code_insee"] for x in published}
    arks = {x["ark_pactols"] for x in published}
    if len(published) != 1195 or len(codes) != 1195 or len(arks) != 1195:
        raise ValueError("Couverture publiée 1195/1228 non vérifiée")
    if {x["code_insee"] for x in registre["dossiers"]} & codes != {"49126"}:
        raise ValueError("Orée d'Anjou doit être le seul des 24 déjà publié")
    selections = []
    for r in registre["dossiers"]:
        cand = r.get("candidat_actuel")
        if r["code_insee"] in codes or cand is None:
            continue
        if cand["situation_URI_INSEE"] == "AUCUN_EXACTMATCH_INSEE":
            selections.append(r)
    if len(selections) != 17 or len({r["code_insee"] for r in selections}) != 17:
        raise ValueError("Attendu : 17 candidats contemporains sans URI INSEE")
    expected = {r["code_insee"]:r["libelle_COG_2026"] for r in selections}
    rdf_concepts, homonyms = analyser_concepts(rdf, expected)
    current = collections.defaultdict(list)
    for p in cog["periodes_com"]:
        if (p["typecom"] == "COM" and p["debut_inclus"] <= "2026-01-01" and
            (p["fin_exclue"] is None or p["fin_exclue"] > "2026-01-01")):
            current[p["code_insee"]].append(p)
    if len(current) != 1228 or any(len(v)!=1 for v in current.values()):
        raise ValueError("Les 1228 COM COG 2026 doivent être uniques")
    rows = []
    for r in sorted(selections,key=lambda r:r["code_insee"]):
        code = r["code_insee"]
        label = r["libelle_COG_2026"]
        cand = r["candidat_actuel"]
        ark = cand["ark"]
        if ark not in rdf_concepts or ark in arks:
            raise ValueError("Concept Pactols actuel absent ou déjà validé : "+ark)
        c = rdf_concepts[ark]
        current_episode = current[code][0]
        exact_insee = [u for u in c["exactMatch"] if u.startswith(INSEE_PREFIX)]
        if (norm(label) not in {norm(x) for x in c["prefLabels_fr"]}
            or exact_insee or cand["exactMatch_INSEE"]
            or c["deprecated"] or c["isReplacedBy"]):
            raise ValueError("ARK non conforme à la présélection : "+ark)
        creation = sorted((m for m in cog["lignes_mouvements_cog"] if
                           m["code_apres"] == code and
                           m["typecom_apres"] == "COM" and
                           m["mod"] == "32" and
                           m["date_effet"] == current_episode["debut_inclus"]),
                          key=lambda m:(m["code_avant"],m["typecom_avant"],m["libelle_avant"]))
        dates = [(p["code_insee"],p["libelle"],p["fin_exclue"])
                 for p in cog["periodes_com"] if
                 p["code_insee"] == code and p["typecom"] == "COM" and
                 p["fin_exclue"] == current_episode["debut_inclus"]]
        cur_match = current_episode["libelle"] == label
        old_ark_separate = r["ark_concept_historique"] != ark and r["ark_concept_historique"] not in arks
        hom = homonyms.get(code,[])
        codes_participants = sorted({m["code_avant"] for m in creation})
        other_id = sorted(u for u in c["exactMatch"] + c["closeMatch"]
                          if not u.startswith(INSEE_PREFIX))
        reasons = []
        if not cur_match:
            reasons.append("LIBELLE_COG_CURRENT_NON_CONCORDANT")
        if not creation:
            reasons.append("CREATION_MOD32_PAS_ATTESTEE_AU_DEBUT")
        if not dates:
            reasons.append("ANCIEN_EPISODE_CODE_NON_DOCUMENTE_A_CETTE_DATE")
        if not old_ark_separate:
            reasons.append("ARK_HISTORIQUE_CONFONDU_OU_DEJA_PUBLIE")
        if len(hom) != 1 or hom != [ark]:
            reasons.append("HOMONYMIE_PACTOLS_PREFLABEL_NON_EXCLUSIVE")
        if other_id:
            reasons.append("IDENTIFIANT_EXTERNE_A_QUALIFIER")
        if c["broader"] or c["related"] or c["definition"] or c["scopeNote"] or c["historyNote"]:
            reasons.append("CONTEXTE_RDF_A_EXAMINER")
        if not reasons:
            classement = "CONCORDANCE_LEXICALE_ET_COG_SANS_PREUVE_D_IDENTITE_PACTOLS"
        elif all(x in {"IDENTIFIANT_EXTERNE_A_QUALIFIER","CONTEXTE_RDF_A_EXAMINER"} for x in reasons):
            classement = "EXAMEN_PREUVES_RDF_COMPLEMENTAIRES"
        else:
            classement = "EXCEPTION_A_INSTRUIRE"
        rows.append({
            "code_insee": code,"libelle_COG_2026":label,"ark_candidat":ark,
            "ark_historique_distinct":r["ark_concept_historique"],
            "prefLabels_fr":c["prefLabels_fr"],"altLabels_fr":c["altLabels_fr"],
            "debut_communale_COG_2026":current_episode["debut_inclus"],
            "historique_meme_code_precedent":dates,
            "creation_mod32_COG":[{"id":m["id"],"date":m["date_effet"],
                                  "code_avant":m["code_avant"],"libelle_avant":m["libelle_avant"],
                                  "type_avant":m["typecom_avant"],
                                  "code_apres":m["code_apres"],"libelle_apres":m["libelle_apres"],
                                  "type_apres":m["typecom_apres"]} for m in creation],
            "codes_communes_anterieures":codes_participants,
            "homonymes_prefLabel_RDF":hom,
            "rdf":{
                "exactMatch_tous":c["exactMatch"],"closeMatch":c["closeMatch"],
                "broader":c["broader"],"related":c["related"],
                "inScheme":c["inScheme"],"definition":c["definition"],
                "scopeNote":c["scopeNote"],"historyNote":c["historyNote"],
                "notes":c["notes"],"deprecated":c["deprecated"],
            },
            "motifs_instruction":reasons,
            "classement_recette":classement,
            "verification_independante":"A_COMPLETER",
            "decision_editoriale":"NON_PRISE","publication":"NON_PUBLIE",
        })
    if len(rows)!=17:
        raise ValueError("Dossiers RDF non exhaustifs")
    groups = collections.Counter(r["classement_recette"] for r in rows)
    reasons = collections.Counter(m for r in rows for m in r["motifs_instruction"])
    return {
        "schema":SCHEMA,"statut":"RECETTE_NON_VALIDANTE",
        "sources":{
            "RDF_Pactols_SHA256":RDF_SHA,
            "COG":"docs/data/lieux-chronologie/cog-pdl.json",
            "mode_COG":"DERIVE_VERSIONNE_VERIFIE_PRECEDEMMENT",
            "registre":"recette/lieux/PDL-24-DIVERGENCES-NOMINATIF-2026.json"},
        "nombre_candidats_sans_URI_INSEE":17,
        "nombre_alignements_publies_precedemment":1195,
        "communes_COG_2026":1228,
        "communes_restant_a_instruire":33,
        "nouveaux_alignements":0,"geometries":0,"successions_inferees":0,
        "groupes":dict(sorted(groups.items())),
        "motifs":dict(sorted(reasons.items())),
        "dossiers":rows,
        "principes":[
            "L'unicité du libellé dans Pactols est une condition nécessaire, pas suffisante.",
            "La création MOD32 INSEE atteste la commune mais pas l'identité du concept Pactols.",
            "Les autres identifiants et relations RDF exigent vérification indépendante.",
            "Les ARK historiques restent distincts et ne sont pas promus.",
            "Le rapport ne crée aucune correspondance ni géométrie publique.",
        ],
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("registre","cog","rdf","base","uuid","lot01",
                 "chemille","lot02","oree","sortie"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    if a.sortie.exists() or "docs" in a.sortie.resolve().parts:
        raise ValueError("Sortie de recette nouvelle et hors répertoire docs")
    load=lambda p: json.loads(p.read_text(encoding="utf-8"))
    out=preparer(load(a.registre),load(a.cog),
                 [load(a.base),load(a.uuid),load(a.lot01),load(a.chemille),
                  load(a.lot02),load(a.oree)],a.rdf)
    a.sortie.parent.mkdir(parents=True,exist_ok=True)
    a.sortie.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
                        encoding="utf-8")
    print("PDL_17_SANS_INSEE_BILAN",json.dumps({
        "groupes":out["groupes"],"motifs":out["motifs"],
        "validations":out["nouveaux_alignements"]},ensure_ascii=False,sort_keys=True))
    for row in out["dossiers"]:
        print("PDL_17_SANS_INSEE_DOSSIER",json.dumps({
          "code":row["code_insee"],"nom":row["libelle_COG_2026"],
          "ark":row["ark_candidat"],"date_COG":row["debut_communale_COG_2026"],
          "homonymes":row["homonymes_prefLabel_RDF"],
          "nb_mouvements_mod32":len(row["creation_mod32_COG"]),
          "codes_anterieurs":row["codes_communes_anterieures"],
          "rdf_exact":row["rdf"]["exactMatch_tous"],"rdf_close":row["rdf"]["closeMatch"],
          "rdf_broader":row["rdf"]["broader"],"rdf_related":row["rdf"]["related"],
          "rdf_note":row["rdf"]["scopeNote"]+row["rdf"]["historyNote"]+row["rdf"]["definition"],
          "classement":row["classement_recette"],
          "motifs":row["motifs_instruction"]
        },ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
