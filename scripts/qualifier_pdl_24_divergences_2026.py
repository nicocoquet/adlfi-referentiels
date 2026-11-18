#!/usr/bin/env python3
"""Recette non validante des 24 divergences Pactols–COG en Pays de la Loire (2026)."""
from __future__ import annotations
import argparse
import collections
import json
import re
from pathlib import Path
from auditer_pactols_cog_regions_prioritaires_2026 import audit, sha, qualifier
from auditer_pactols_polynesie_2026 import RDF_SHA, label_compatible, norm, analyser_rdf
from qualifier_pdl_ark_multiples_2026 import completer_rdf

SCHEMA = "adlfi.lieux.pdl.24-divergences.2026.recette.v1"
PUBLICATIONS = (
    "pactols-pdl-2026.json",
    "pactols-pdl-uuid-resolus-2026.json",
    "pactols-pdl-communes-nouvelles-lot01-2026.json",
    "pactols-pdl-chemille-2026.json",
    "pactols-pdl-communes-nouvelles-lot02-2026.json",
)
URI_PREFIX = "http://id.insee.fr/geo/commune/"
INSEE_PREFIXES = ("http://id.insee.fr/geo/", "https://id.insee.fr/geo/")

def anciennes_denom(cog: dict, code: str, libelle: str) -> list[dict]:
    return sorted((
        {"debut": p["debut_inclus"], "fin": p["fin_exclue"],
         "libelle": p["libelle"], "typecom": p["typecom"]}
        for p in cog["periodes_com"] if p["code_insee"] == code and
        p["typecom"] == "COM" and label_compatible(p["libelle"], libelle)
    ), key=lambda p: p["debut"])

def analyser_dossier(row: dict, complement: dict, cog: dict) -> dict:
    code = row["code"]
    label = row["nom"]
    hits = row["preuves_RDF_exactMatch"]
    if len(hits) != 1:
        raise ValueError("Un seul concept RDF attendu pour la divergence : " + code)
    p = hits[0]
    ark = p["ark"]
    extra = complement[ark]
    reasons = []
    if p["deprecie"]:
        reasons.append("CONCEPT_DEPRECIE")
    if p["remplace"] or extra["remplacements_explicites"]:
        reasons.append("CONCEPT_REMPLACE")
    if p["risque_ile_atoll_autre_type"]:
        reasons.append("PREFIXE_TYPE_GEOGRAPHIQUE_A_QUALIFIER")
    if len(p["prefLabels_fr"]) != 1:
        reasons.append("PREFLABEL_NON_UNIVOQUE")
    if not any(label_compatible(label, x) for x in p["prefLabels_fr"]):
        reasons.append("PREFLABEL_NON_CONCORDANT")
    if len(p["codes_communaux_cites"]) != 1:
        reasons.append("ARK_ASSOCIE_A_PLUSIEURS_CODES_COG")
    uri = URI_PREFIX + code
    insee = sorted(u for u in extra["exactMatch_tous"]
                   if u.startswith(INSEE_PREFIXES))
    autres = [u for u in insee if u != uri]
    if uri not in insee:
        reasons.append("URI_INSEE_COURANTE_ABSENTE_DU_RDF")
    if autres:
        if any(re.search(r"/[a-f0-9]{8}-[a-f0-9-]{27,36}$", u, re.I) for u in autres):
            reasons.append("URI_INSEE_UUID_SUPPLEMENTAIRE")
        reasons.append("AUTRE_URI_INSEE_SUPPLEMENTAIRE")
    if any(x["famille"] != "commune" or x["code"] != code
           for x in p["insee_exactMatch"]):
        reasons.append("AUTRE_CODE_INSEE_INTERPRETABLE")
    # Une altLabel ou un ancien libellé concordants sont des indices, jamais des preuves.
    alts_compatibles = [x for x in p["altLabels_fr"]
                        if label_compatible(label, x)]
    anciens = [
        {"libelle": pref, "episodes": anciennes_denom(cog, code, pref)}
        for pref in p["prefLabels_fr"]
        if norm(pref) != norm(label)
    ]
    candidats_lexicaux = []
    for possible in row["candidats_lexicaux_non_validants"]:
        c_ark = possible["ark"]
        full = complement[c_ark]
        links = [u for u in full["exactMatch_tous"]
                 if u.startswith(INSEE_PREFIXES)]
        if uri in links:
            state = "URI_INSEE_COURANTE_POTENTIELLE_A_VERIFIER"
        elif links:
            state = ("URI_INSEE_UUID_A_RESoudre"
                     if any(re.search(r"/[a-f0-9]{8}-[a-f0-9-]{27,36}$", u, re.I)
                            for u in links)
                     else "URI_INSEE_AUTRE_CODE_OU_TYPE")
        else:
            state = "AUCUN_EXACTMATCH_INSEE"
        candidats_lexicaux.append({
            "ark": c_ark, "prefLabels_fr": possible["prefLabels_fr"],
            "exactMatch_INSEE_parsees": possible["exactMatch_INSEE"],
            "exactMatch_INSEE_completes": links,
            "autres_exactMatch": [u for u in full["exactMatch_tous"]
                                  if u not in links],
            "remplacements_explicites": full["remplacements_explicites"],
            "definitions": full["definitions"],
            "notes_portee": full["notes_portee"],
            "situation_URI_INSEE": state,
            "decision_editoriale": "NON_PRISE"
        })
    candidats_lexicaux.sort(key=lambda p:p["ark"])
    if not reasons:
        raise ValueError("La règle d'audit initiale aurait dû accepter " + code)
    anciens_attestes = [x for x in anciens if x["episodes"] and
                       all(e["fin"] is not None and e["fin"] <= "2026-01-01"
                           for e in x["episodes"])]
    if (len(anciens_attestes) == 1 and not alts_compatibles and
        reasons == ["PREFLABEL_NON_CONCORDANT"]):
        groupe = "PREFLABEL_HISTORIQUE_COG"
    elif p["deprecie"] or p["remplace"] or extra["remplacements_explicites"]:
        groupe = "STATUT_OU_REMPLACEMENT"
    elif autres or len(p["codes_communaux_cites"]) != 1:
        groupe = "URI_OU_CODES_CONCURRENTS"
    elif p["risque_ile_atoll_autre_type"]:
        groupe = "TYPE_GEOGRAPHIQUE_A_VERIFIER"
    elif "PREFLABEL_NON_CONCORDANT" in reasons:
        groupe = "LIBELLE_NON_CONCORDANT"
    else:
        groupe = "STRUCTURE_RDF_ATYPIQUE"
    return {
        "code_COG_2026": code, "nom_COG_2026": label,
        "departement": row["departement"], "ark_pactols": ark,
        "prefLabels_fr": p["prefLabels_fr"],
        "altLabels_fr": p["altLabels_fr"],
        "altLabels_compatibles": alts_compatibles,
        "codes_communaux_cites": p["codes_communaux_cites"],
        "insee_exactMatch_parsees": p["insee_exactMatch"],
        "insee_exactMatch_completes": insee,
        "autres_exactMatch_non_INSEE": [
            x for x in extra["exactMatch_tous"] if x not in insee
        ],
        "rdf": {
            "deprecie": p["deprecie"], "remplace": p["remplace"],
            "remplacements": extra["remplacements_explicites"],
            "definitions": extra["definitions"],
            "notes_histoire": extra["notes_histoire"],
            "notes_portee": extra["notes_portee"],
            "notes": extra["notes"],
        },
        "episodes_COG_meme_code": sorted((
            {"libelle": x["libelle"], "debut": x["debut_inclus"],
             "fin": x["fin_exclue"]}
            for x in cog["periodes_com"]
            if x["code_insee"] == code and x["typecom"] == "COM"
        ), key=lambda r: r["debut"]),
        "prefLabels_anciens_eventuels": anciens,
        "prefLabels_anciens_attestes_COG": anciens_attestes,
        "candidats_lexicaux_sans_exactMatch_courant": candidats_lexicaux,
        "altLabel_pouvant_designER_2026": bool(alts_compatibles),
        "motifs": sorted(set(reasons)),
        "groupe_instruction": groupe,
        "ark_retenu": None, "decision_editoriale": "NON_PRISE",
        "publication": "NON_PUBLIE",
    }

def audit_depuis_cog_versionne(rdf: Path, pdl: dict, corse: dict,
                               bfc: dict) -> dict:
    """Recette basée sur les trois éditions COG publiées et déjà contrôlées.

    Ce mode est un contrôle de reproductibilité des dérivés COG, NON une
    nouvelle vérification du SHA-256 des fichiers CSV officiels en ligne.
    """
    if sha(rdf) != RDF_SHA:
        raise ValueError("Le RDF Pactols ne correspond pas au SHA épinglé")
    regions = (
        ("52", "pdl", pdl, 1228),
        ("94", "corse", corse, 360),
        ("27", "bfc", bfc, 3685),
    )
    names, rows_data, stats = {}, {}, {}
    for code_region,slug,data,expected in regions:
        if data.get("region") != slug or data.get("millesime_cog") != 2026:
            raise ValueError("Édition COG dérivée inattendue : " + slug)
        current = [p for p in data["periodes_com"]
                   if p["typecom"] == "COM" and
                   p["debut_inclus"] <= "2026-01-01" and
                   (p["fin_exclue"] is None or p["fin_exclue"] > "2026-01-01")]
        if len(current) != expected:
            raise ValueError("Effectif régional COG inattendu : " + slug)
        for p in current:
            code = p["code_insee"]
            if code in names:
                raise ValueError("Code COG dupliqué entre régions : " + code)
            names[code] = p["libelle"]
            rows_data[code] = (code_region,p["libelle"])
        stats[code_region] = {"communes_COG_2026": expected}
    if len(names) != 5273:
        raise ValueError("Régions COG versionnées incomplètes")
    scanned = analyser_rdf(rdf,names)
    rows = []
    for code,(region,nom) in sorted(rows_data.items()):
        hits = scanned["explicites"][code]
        rows.append({
            "code": code,"nom": nom,"region": region,"departement": code[:2],
            "etat": qualifier(code,nom,hits),
            "preuves_RDF_exactMatch":hits,
            "candidats_lexicaux_non_validants":
              scanned["lexicaux_sans_exactMatch_987"].get(code,[]),
        })
    counts = collections.Counter(r["etat"] for r in rows if r["region"]=="52")
    if counts != {"ELIGIBLE_SELON_REGLE":1140,
                  "A_INSTRUIRE_PLUSIEURS_ARK":60,
                  "A_INSTRUIRE_LIBELLE_STATUT_OU_URI":24,
                  "SANS_EXACTMATCH":4}:
        raise ValueError("La répartition PDL diffère de l'audit officiel initial : "+str(counts))
    return {"pactols":{"sha256":RDF_SHA},
            "cog":{"sha256":"7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3",
                   "mode":"COG_2026_DERIVES_VERSIONNES_SANS_NOUVEAU_TELECHARGEMENT"},
            "regions":stats,"communes":rows}

def rapport(rdf: Path, cog_courant: Path | None, chronologie: dict,
            publications: list[dict], corse: dict | None = None,
            bfc: dict | None = None) -> dict:
    published = [a for p in publications
                 for a in p["alignements_Pactols_COG_valides_2026"]]
    codes = {a["code_insee"] for a in published}
    arks = {a["ark_pactols"] for a in published}
    if len(published) != 1194 or len(codes) != 1194 or len(arks) != 1194:
        raise ValueError("La publication PDL doit compter 1 194 correspondances uniques")
    a = (audit(rdf,cog_courant) if cog_courant is not None else
         audit_depuis_cog_versionne(rdf,chronologie,corse,bfc))
    if a["pactols"]["sha256"] != RDF_SHA or a["regions"]["52"]["communes_COG_2026"] != 1228:
        raise ValueError("Source RDF/COG inattendue")
    subset = [r for r in a["communes"] if r["region"] == "52" and
              r["etat"] == "A_INSTRUIRE_LIBELLE_STATUT_OU_URI"]
    if len(subset) != 24 or len({r["code"] for r in subset}) != 24:
        raise ValueError("La catégorie de divergence doit compter exactement 24 codes")
    if any(r["code"] in codes for r in subset):
        raise ValueError("Des divergences sont déjà publiées dans les 1194")
    complements = completer_rdf(rdf, {
        p["ark"] for r in subset
        for p in (r["preuves_RDF_exactMatch"] + r["candidats_lexicaux_non_validants"])
    })
    dossiers = [analyser_dossier(r, complements, chronologie) for r in subset]
    dossiers.sort(key=lambda r: (r["groupe_instruction"], r["code_COG_2026"]))
    counts = collections.Counter(x["groupe_instruction"] for x in dossiers)
    motifs = collections.Counter(m for x in dossiers for m in x["motifs"])
    types_candidats = collections.Counter(
        p["situation_URI_INSEE"] for row in dossiers
        for p in row["candidats_lexicaux_sans_exactMatch_courant"]
    )
    noms_courants_candidats = sum(bool(r["candidats_lexicaux_sans_exactMatch_courant"])
                                 for r in dossiers)
    return {
        "schema": SCHEMA, "statut": "RECETTE_NON_VALIDANTE",
        "sources": {"pactols_sha256": RDF_SHA,
                    "cog_sha256": a["cog"]["sha256"],
                    "mode_COG": a["cog"].get("mode","CSV_OFFICIEL_SHA_VERIFIE")},
        "nombre_dossiers": 24, "publication_PDL_2026_existante": 1194,
        "exception_PDL_existantes": 34,
        "nouvelles_validations": 0, "geometries": 0,
        "liens_historiques_inferes": 0,
        "groupes": dict(sorted(counts.items())),
        "motifs": dict(sorted(motifs.items())),
        "communes_avec_candidat_lexical": noms_courants_candidats,
        "types_URI_candidats_lexicaux": dict(sorted(types_candidats.items())),
        "dossiers": dossiers,
        "regles": [
            "Une altLabel concordante ne valide pas un concept.",
            "Une URI INSEE supplémentaire impose l'instruction de sa portée.",
            "Une concordance avec un ancien libellé COG n'établit pas une succession ARK.",
            "Aucun dossier n'est publié depuis ce rapport de recette.",
        ],
    }

def registre_nominatif(d: dict) -> dict:
    """Projection stable à conserver dans Git, tandis que le rapport probatoire
    complet et ses notes RDF restent dans l'artefact de recette."""
    dossiers = []
    for row in sorted(d["dossiers"],key=lambda x:x["code_COG_2026"]):
        anciens = row["prefLabels_anciens_attestes_COG"]
        if len(anciens) != 1 or len(anciens[0]["episodes"]) != 1:
            raise ValueError("Ancien épisode COG non univoque : "+row["code_COG_2026"])
        old = anciens[0]
        candidates = row["candidats_lexicaux_sans_exactMatch_courant"]
        if len(candidates)>1:
            raise ValueError("Plusieurs candidats contemporains : "+row["code_COG_2026"])
        dossiers.append({
            "code_insee":row["code_COG_2026"],
            "libelle_COG_2026":row["nom_COG_2026"],
            "ark_concept_historique":row["ark_pactols"],
            "prefLabel_historique":old["libelle"],
            "fin_dernier_episode_COM_historique":old["episodes"][0]["fin"],
            "candidat_actuel":({
                "ark":candidates[0]["ark"],
                "prefLabels_fr":candidates[0]["prefLabels_fr"],
                "situation_URI_INSEE":candidates[0]["situation_URI_INSEE"],
                "exactMatch_INSEE":candidates[0]["exactMatch_INSEE_completes"],
            } if candidates else None),
            "decision_editoriale":"NON_PRISE",
            "publication":"NON_PUBLIE",
        })
    if len(dossiers) != 24:
        raise ValueError("Registre nominatif différent de 24 dossiers")
    return {
        "schema":"adlfi.lieux.pdl.24-divergences.2026.registre-non-validant.v1",
        "statut":"RECETTE_NON_VALIDANTE",
        "source_RDF_Pactols_sha256":RDF_SHA,
        "source_COG": "trois_COG_2026_derives_versionnes",
        "nombre_dossiers":24,
        "communes_avec_candidat":sum(bool(r["candidat_actuel"]) for r in dossiers),
        "communes_sans_candidat":sum(not r["candidat_actuel"] for r in dossiers),
        "nouvelles_validations":0,
        "dossiers":dossiers
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for n in ("rdf","chronologie","base","uuid","lot01",
              "chemille","lot02","sortie"):
        p.add_argument("--"+n, type=Path, required=True)
    p.add_argument("--cog-officiel",type=Path)
    p.add_argument("--corse",type=Path)
    p.add_argument("--bfc",type=Path)
    p.add_argument("--registre-nominatif",type=Path)
    args = p.parse_args()
    if args.sortie.exists() or "docs" in args.sortie.resolve().parts:
        raise ValueError("Sortie de recette non existante, hors docs")
    read = lambda f: json.loads(f.read_text(encoding="utf-8"))
    if args.cog_officiel is None and (args.corse is None or args.bfc is None):
        raise ValueError("Le mode COG versionné exige --corse et --bfc")
    d = rapport(args.rdf,args.cog_officiel,read(args.chronologie),
                [read(args.base),read(args.uuid),read(args.lot01),
                 read(args.chemille),read(args.lot02)],
                read(args.corse) if args.corse else None,
                read(args.bfc) if args.bfc else None)
    args.sortie.parent.mkdir(parents=True,exist_ok=True)
    args.sortie.write_text(json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
                           encoding="utf-8")
    if args.registre_nominatif:
        if args.registre_nominatif.exists():
            raise ValueError("Ne pas écraser un registre nominatif")
        args.registre_nominatif.parent.mkdir(parents=True,exist_ok=True)
        args.registre_nominatif.write_text(json.dumps(registre_nominatif(d),
              ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n",
              encoding="utf-8")
    print("PDL_24_DIVERGENCES_GROUPES",
          json.dumps(d["groupes"],ensure_ascii=False,sort_keys=True))
    print("PDL_24_DIVERGENCES_MOTIFS",
          json.dumps(d["motifs"],ensure_ascii=False,sort_keys=True))
    print("PDL_24_CANDIDATS_LEXICAUX",json.dumps({
        "communes":d["communes_avec_candidat_lexical"],
        "types_URI":d["types_URI_candidats_lexicaux"]},sort_keys=True))
    for row in d["dossiers"]:
        print("PDL_24_DIVERGENCE",json.dumps({
            "code":row["code_COG_2026"],"nom":row["nom_COG_2026"],
            "ark":row["ark_pactols"],"pref":row["prefLabels_fr"],
            "alt_cog":row["altLabels_compatibles"],
            "groupe":row["groupe_instruction"],"motifs":row["motifs"],
            "uri_insee":row["insee_exactMatch_completes"],
            "episodes_COG":row["episodes_COG_meme_code"],
            "anciens_attestes":row["prefLabels_anciens_attestes_COG"],
            "candidats_lexicaux":row["candidats_lexicaux_sans_exactMatch_courant"],
        },ensure_ascii=False,sort_keys=True))
if __name__=="__main__":
    main()
