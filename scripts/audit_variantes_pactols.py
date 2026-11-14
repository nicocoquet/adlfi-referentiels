#!/usr/bin/env python3
"""Audit reproductible des variantes SKOS de Pactols Lieux pour les 103 ARK PACA.

Lecture seule : ne modifie aucun fichier publié. Sorties candidates non validées.
"""
import argparse
import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

SOURCE_REPO = "frantiq/PACTOLS"
SOURCE_COMMIT = "69bf9697e24cefd645a69465bbd271702786285a"
SOURCE_PATH = "pactols-latest-version/pactols_lieux_all/Pactols_Lieux_th17_20260722.rdf"
SOURCE_SHA256 = "3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7"
SKOS = "{http://www.w3.org/2004/02/skos/core#}"
RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
XML = "{http://www.w3.org/XML/1998/namespace}"
OWL = "{http://www.w3.org/2002/07/owl#}"
DCT = "{http://purl.org/dc/terms/}"
URI_PREFIX = "https://ark.frantiq.fr/ark:/"
LANGUAGE = re.compile(r"^[a-z]{2,3}(?:-[a-z0-9]{2,8})*$", re.I)


def empreinte(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for bloc in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloc)
    return h.hexdigest()


def arks_pilote(lieux_json):
    data = json.loads(Path(lieux_json).read_text(encoding="utf-8"))
    if (data.get("module") != "lieux" or data.get("perimetre") != "PACA"
            or data.get("schema_version") != "0.1.0"
            or data.get("statut_publication") != "pilote_valide"):
        raise ValueError("Contrat du pilote PACA inattendu")
    autorites = data.get("autorites")
    if not isinstance(autorites, list) or len(autorites) != 103:
        raise ValueError("103 autorités validées attendues")
    par_ark = {}
    for a in autorites:
        ark = a["ark_pactols"]
        if (not re.fullmatch(r"26678/[A-Za-z0-9]+", ark)
                or ark in par_ark or a["type_entite"] != "commune"
                or len(a["correspondances"]) != 1
                or a["correspondances"][0]["validation"]["statut"]
                   != "VALIDE_EDITEUR_2026_10_18"):
            raise ValueError("Autorité PACA non conforme : " + ark)
        par_ark[ark] = a
    return par_ark


def lire_rdf(rdf_path, arks):
    """Parser l'export RDF/XML en streaming, sans rapprochement par homonymie."""
    attendus = {URI_PREFIX + ark: ark for ark in arks}
    trouves, anomalies = {}, []
    contexte = ET.iterparse(rdf_path, events=("start", "end"))
    _, racine = next(contexte)
    if racine.tag != RDF + "RDF":
        raise ValueError("Source non reconnue comme RDF/XML")
    for event, noeud in contexte:
        if event != "end" or noeud.tag not in (RDF + "Description", SKOS + "Concept"):
            continue
        uri = noeud.get(RDF + "about")
        ark = attendus.get(uri)
        if ark:
            if ark in trouves:
                anomalies.append({"ark": ark, "type": "description_doublon"})
                noeud.clear()
                racine.clear()
                continue
            types = {x.get(RDF + "resource") for x in noeud.findall(RDF + "type")}
            est_concept = (noeud.tag == SKOS + "Concept" or
                           "http://www.w3.org/2004/02/skos/core#Concept" in types)
            pref, variantes, deja = {}, [], set()
            for element in noeud:
                if element.tag in (SKOS + "altLabel", SKOS + "prefLabel"):
                    libelle = element.text or ""
                    lang = element.get(XML + "lang", "")
                    if not libelle.strip() or not LANGUAGE.fullmatch(lang):
                        anomalies.append({
                            "ark": ark, "type": "libelle_skos_inexploitable",
                            "propriete": "altLabel" if element.tag == SKOS + "altLabel" else "prefLabel",
                        })
                        continue
                    if element.tag == SKOS + "prefLabel":
                        pref.setdefault(lang, []).append(libelle)
                    elif (lang, libelle) not in deja:
                        deja.add((lang, libelle))
                        variantes.append({
                            "libelle": libelle, "langue": lang,
                            "type": "skos:altLabel", "uri_source": uri,
                        })
                if element.tag == OWL + "deprecated" and (element.text or "").strip().lower() in ("true", "1"):
                    anomalies.append({"ark": ark, "type": "concept_deprecie"})
                if element.tag == DCT + "isReplacedBy":
                    anomalies.append({"ark": ark, "type": "concept_remplace"})
            if not est_concept:
                anomalies.append({"ark": ark, "type": "ressource_non_concept"})
            trouves[ark] = {
                "est_concept": est_concept,
                "pref_labels": pref,
                "variantes": sorted(variantes, key=lambda v: (v["langue"], v["libelle"].casefold())),
            }
        noeud.clear()
        racine.clear()
    return trouves, anomalies


def produire(lieux_json, rdf_path, verification_source=True):
    fichier = Path(rdf_path)
    if not fichier.is_file():
        raise FileNotFoundError(fichier)
    sha = empreinte(fichier)
    if verification_source and sha != SOURCE_SHA256:
        raise ValueError("Empreinte SHA-256 de Pactols Lieux différente de la source épinglée")
    par_ark = arks_pilote(lieux_json)
    trouves, anomalies = lire_rdf(fichier, par_ark)
    candidats, lignes = [], []
    hors_concept = {x["ark"] for x in anomalies if x["type"] in (
        "concept_deprecie", "concept_remplace", "ressource_non_concept")}
    compte_langues = Counter()
    concordances_pref = 0
    avec_variantes = 0
    for ark, a in sorted(par_ark.items(), key=lambda e: (e[1]["libelle_pactols"].casefold(), e[0])):
        info = trouves.get(ark)
        variantes = info["variantes"] if info else []
        fr = info["pref_labels"].get("fr", []) if info else []
        concordant = a["libelle_pactols"] in fr
        if info and fr and not concordant:
            anomalies.append({
                "ark": ark, "type": "pref_label_fr_different",
                "editorial": a["libelle_pactols"], "source": fr,
            })
        if concordant:
            concordances_pref += 1
        if variantes:
            avec_variantes += 1
        compte_langues.update(v["langue"] for v in variantes)
        candidats.append({
            "ark_pactols": ark,
            "libelle_pactols": a["libelle_pactols"],
            "trouve_dans_export": info is not None,
            "pref_labels_source": info["pref_labels"] if info else {},
            "a_instruire": ark in hors_concept or bool(fr and not concordant),
            "variantes_pactols": variantes,
        })
        if not info:
            anomalies.append({"ark": ark, "type": "ark_absent_export"})
        if not variantes:
            lignes.append([ark, a["libelle_pactols"], "", "",
                           "aucune_variante_attestee" if info else "ark_absent"])
        else:
            for v in variantes:
                lignes.append([ark, a["libelle_pactols"], v["langue"], v["libelle"], "a_valider"])
    resume = {
        "nombre_ark_pilote": len(par_ark),
        "nombre_ark_trouves": len(trouves),
        "nombre_ark_absents": len(par_ark) - len(trouves),
        "nombre_ark_avec_variantes": avec_variantes,
        "nombre_variantes_attestees": sum(compte_langues.values()),
        "langues": dict(sorted(compte_langues.items())),
        "pref_label_fr_identique": concordances_pref,
        "anomalies_par_type": dict(sorted(Counter(x["type"] for x in anomalies).items())),
    }
    rapport = {
        "statut": "candidats_non_valides",
        "origine": {
            "institution": "CNRS-Frantiq",
            "depot": SOURCE_REPO, "commit": SOURCE_COMMIT,
            "chemin": SOURCE_PATH,
            "sha256_attendu": SOURCE_SHA256, "sha256_observe": sha,
            "format": "RDF/XML SKOS", "thesaurus": "th17",
            "date_nom_export": "2026-07-22",
            "url": f"https://github.com/{SOURCE_REPO}/blob/{SOURCE_COMMIT}/{SOURCE_PATH}",
            "licence": "ODbL-1.0",
        },
        "resume": resume,
        "anomalies": sorted(anomalies, key=lambda x: (x["ark"], x["type"])),
        "note": "Candidats non validés. Une absence dans l'export daté n'implique pas une absence dans Pactols vivant.",
    }
    return rapport, candidats, lignes


def ecrire(rapport, candidats, lignes, output_dir):
    sortie = Path(output_dir).resolve()
    if sortie == (Path(__file__).resolve().parents[1] / "docs/data").resolve():
        raise ValueError("Publication directe dans docs/data interdite")
    sortie.mkdir(parents=True, exist_ok=True)
    (sortie / "rapport-pactols-lieux.json").write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (sortie / "candidats-variantes-pactols.json").write_text(
        json.dumps(candidats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (sortie / "revue-variantes-pactols.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["ark_pactols", "libelle_pactols", "langue", "variante", "statut_revue"])
        w.writerows(lignes)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-rdf", type=Path, required=True)
    p.add_argument("--lieux-json", type=Path, default=Path("docs/data/lieux.json"))
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    rapport, candidats, lignes = produire(args.lieux_json, args.source_rdf)
    ecrire(rapport, candidats, lignes, args.output_dir)
    print("SOURCE Pactols Lieux vérifiée : " + rapport["origine"]["sha256_observe"])
    print("RAPPORT " + json.dumps(rapport["resume"], ensure_ascii=False, sort_keys=True))
    print("SORTIES NON PUBLIÉES : " + str(args.output_dir))


if __name__ == "__main__":
    main()
