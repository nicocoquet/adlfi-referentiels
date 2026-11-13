#!/usr/bin/env python3
"""Inventorier des XML AdlFI et extraire leurs index Pactols:Lieux.

Lecture seule du corpus. Aucune géolocalisation ni validation COG inférée.
Python >= 3.9, bibliothèque standard uniquement.

Exemple :
    python3 scripts/extraire_lieux_xml_adlfi.py \
      "$HOME/sDrive/DR05_USR3225_ADLFI/AdlFI_NOTICES-FAITES" \
      --output-dir "$HOME/Desktop/AdlFI-audit-lieux"
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

TEI = "{http://www.tei-c.org/ns/1.0}"
XML = "{http://www.w3.org/XML/1998/namespace}"
ARK_RE = re.compile(r"^26678/[A-Za-z0-9]+$")
FULL_ARK_RE = re.compile(r"^https?://ark\.frantiq\.fr/ark:/((?:26678)/[A-Za-z0-9]+)$", re.I)
YEAR_RE = re.compile(r"(?<!\d)(?:18|19|20)\d{2}(?!\d)")
MAIN_CSV_FIELDS = (
    "notice_id", "fichier_relatif", "numero_notice", "xml_id", "titre", "sous_titre",
    "annees_operation", "dates_operation_brutes", "presence_intervalle", "source_annees",
    "nombre_ark_terminaux", "nombre_occurrences_lieux", "nombre_index_lieux", "qualite", 
)
OCC_CSV_FIELDS = (
    "notice_id", "fichier_relatif", "numero_notice", "numero_occurrence", "ark_terminal",
    "libelle_terminal_fr", "libelle_original_index", "chaine_ark", "chaine_libelles_fr",
    "profondeur", "zone_tei", "source_brute", "annees_operation", "qualite",
)
AUTH_CSV_FIELDS = (
    "ark_pactols", "libelle_fr_xml", "nombre_notices_distinctes", "nombre_occurrences",
    "nombre_fichiers", "annees_operation_relevees", "premiere_annee_relevee",
    "derniere_annee_relevee", "notices_sans_annee", "alignement_pilote",
    "code_insee_2026_valide", "nom_cog_2026_valide",
)
ALIGN_CSV_FIELDS = (
    "ark_pactols", "libelle_fr_xml", "nombre_notices_distinctes",
    "statut", "code_insee_2026", "nom_cog_2026", "source_validation",
)
INV_CSV_FIELDS = ("fichier_relatif", "taille_octets", "decision", "raison", "sha256", "notices", "erreur")


def normaliser_nom(nom: str) -> str:
    """Normalisation uniquement pour la détection d'Édito/Éditos."""
    s = unicodedata.normalize("NFKD", nom.casefold())
    return "".join(c for c in s if not unicodedata.combining(c))


def retenir_fichier(p: Path) -> tuple[bool, str]:
    if p.suffix.lower() != ".xml":
        return False, "hors_extension_xml"
    if "adlfi" not in p.name.casefold():
        return False, "nom_sans_adlfi"
    if "edito" in normaliser_nom(p.name):
        return False, "nom_edito_exclu"
    if p.is_symlink():
        return False, "fichier_lien_symbolique"
    return True, "inclus"


def inventaire(racine: Path) -> list[dict]:
    """Explorer récursivement les XML, avec chemin relatif et exclusions motivées."""
    lignes = []
    for p in sorted(racine.rglob("*"), key=lambda x: x.relative_to(racine).as_posix().casefold()):
        if not p.is_file() and not p.is_symlink():
            continue
        if p.suffix.lower() != ".xml":
            continue
        inclure, motif = retenir_fichier(p)
        lignes.append({
            "path": p, "fichier_relatif": p.relative_to(racine).as_posix(),
            "taille_octets": p.stat().st_size if not p.is_symlink() else "",
            "decision": "inclu" if inclure else "exclu", "raison": motif,
            "sha256": "", "notices": "", "erreur": "",
        })
    return lignes


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def enfants(elem: ET.Element, nom: str) -> list[ET.Element]:
    return [x for x in elem if local(x.tag) == nom]


def texte_visible(elem: ET.Element | None) -> str:
    """Exclut les index Pactols multilingues, garde le term orig du titre."""
    if elem is None:
        return ""
    bouts = []

    def visite(e: ET.Element) -> None:
        if local(e.tag) == "index" and (e.get("indexName", "").startswith("pactols:")):
            return
        if e.text:
            bouts.append(e.text)
        for child in e:
            visite(child)
            if child.tail:
                bouts.append(child.tail)

    visite(elem)
    return " ".join("".join(bouts).split())


def libelle_fr(index: ET.Element) -> str:
    termes = enfants(index, "term")
    for term in termes:
        if term.get(XML + "lang", "").casefold().startswith("fr"):
            return " ".join("".join(term.itertext()).split())
    return ""


def extraire_ark(source: str | None) -> str | None:
    if not source:
        return None
    s = source.strip()
    if ARK_RE.fullmatch(s):
        return s
    m = FULL_ARK_RE.fullmatch(s)
    return m.group(1) if m else None


def terminales(index_racine: ET.Element):
    """Une occurrence par feuille de chaîne hiérarchique indexée."""
    def marche(noeud: ET.Element, chaine: list[ET.Element]):
        chemin = [*chaine, noeud]
        dessous = enfants(noeud, "index")
        if dessous:
            for child in dessous:
                yield from marche(child, chemin)
        else:
            yield chemin
    yield from marche(index_racine, [])


def element_zone(noeud: ET.Element, parents: dict[ET.Element, ET.Element]) -> str:
    p = noeud
    while p in parents:
        p = parents[p]
        if local(p.tag) in ("head", "p", "ab", "note", "figure", "table"):
            return local(p.tag)
    return "autre"


def detecter_intervalles(texte: str) -> bool:
    # On ne développe jamais des bornes en années intermédiaires implicites.
    return bool(re.search(r"\b(?:18|19|20)\d{2}\s*[-–—/]\s*(?:18|19|20)\d{2}\b", texte))


def annees_notice(notice: ET.Element):
    blocs = [e for e in notice.iter()
             if local(e.tag) == "ab" and e.get("type", "").casefold() == "meta-archeo"]
    annees, bruts, origine = set(), [], []
    intervalle = False
    for bloc in blocs:
        texte = " ".join("".join(bloc.itertext()).split())
        # Certains ab meta-archeo contiennent d'autres métadonnées : année
        # obligatoire uniquement si un libellé d'opération ou un date existe.
        dates = [e for e in bloc.iter() if local(e.tag) == "date"]
        if not dates and not re.search(
            r"(?:ann[ée]es?|dates?)\s+(?:de\s+|des\s+|d[’']\s*)?(?:l[’']\s*)?op[ée]rations?",
            texte, re.I,
        ):
            continue
        if texte:
            bruts.append(texte)
        for e in dates:
            valeurs = ["".join(e.itertext()).strip()]
            valeurs.extend(e.get(k, "") for k in ("when", "from", "to", "notBefore", "notAfter"))
            for valeur in valeurs:
                annees.update(int(x) for x in YEAR_RE.findall(valeur))
            if e.get("from") or e.get("to") or e.get("notBefore") or e.get("notAfter"):
                intervalle = True
        if not dates:
            annees.update(int(x) for x in YEAR_RE.findall(texte))
        intervalle |= detecter_intervalles(texte)
        origine.append("ab[@type=meta-archeo]")
    return sorted(annees), bruts, intervalle, "|".join(sorted(set(origine)))


def extraire_notice(notice: ET.Element, relatif: str, numero: int):
    notice_id = f"{relatif}::notice-{numero:06d}"
    heads = [e for e in notice if local(e.tag) == "head"]
    titres = [e for e in heads if e.get("type") not in ("sub", "subtitle")]
    sous_titres = [e for e in heads if e.get("type") in ("sub", "subtitle")]
    titre = texte_visible(titres[0]) if titres else (texte_visible(heads[0]) if heads else "")
    sous_titre = texte_visible(sous_titres[0]) if sous_titres else ""
    annees, annees_brutes, intervalle, source_annees = annees_notice(notice)
    parents = {child: parent for parent in notice.iter() for child in parent}
    racines = [e for e in notice.iter() if local(e.tag) == "index"
               and e.get("indexName") == "pactols:Lieux"]
    occurrences, anomalies = [], []
    for index in racines:
        # Original de la zone TEI (pas les traductions sur la chaîne Pactols).
        contexte = parents.get(index)
        original = ""
        if contexte is not None and local(contexte.tag) == "index":
            original = " ".join(" ".join("".join(t.itertext()).split()) for t in enfants(contexte, "term")
                                 if t.get("type") == "orig").strip()
        for chemin in terminales(index):
            arks = [extraire_ark(x.get("source")) for x in chemin]
            if arks[-1] is None:
                anomalies.append({"notice_id": notice_id, "type": "ark_terminal_invalide",
                                  "source": chemin[-1].get("source", "")})
                continue
            chemin_partiel = any(a is None for a in arks)
            if chemin_partiel:
                anomalies.append({"notice_id": notice_id, "type": "ark_ancetre_invalide",
                                  "sources": [x.get("source", "") for x in chemin]})
            final = chemin[-1]
            if not libelle_fr(final):
                anomalies.append({"notice_id": notice_id,
                                  "type": "libelle_fr_terminal_absent", "ark": arks[-1]})
            occurrences.append({
                "notice_id": notice_id,
                "fichier_relatif": relatif,
                "numero_notice": numero,
                "numero_occurrence": len(occurrences) + 1,
                "ark_terminal": arks[-1],
                "libelle_terminal_fr": libelle_fr(final),
                "libelle_original_index": original,
                "chaine_ark": json.dumps([a for a in arks if a is not None], ensure_ascii=False),
                "chaine_libelles_fr": json.dumps([libelle_fr(e) for e in chemin], ensure_ascii=False),
                "profondeur": len(chemin),
                "zone_tei": element_zone(index, parents),
                "source_brute": final.get("source", ""),
                "annees_operation": json.dumps(annees),
                "qualite": "hierarchie_partielle" if chemin_partiel else "ok",
            })
    if not racines:
        anomalies.append({"notice_id": notice_id, "type": "aucun_index_pactols_lieux"})
    if not annees:
        anomalies.append({"notice_id": notice_id, "type": "annee_operation_absente"})
    if intervalle:
        anomalies.append({"notice_id": notice_id, "type": "intervalle_annees_non_developpe"})
    if not titre:
        anomalies.append({"notice_id": notice_id, "type": "titre_notice_absent"})
    notice_row = {
        "notice_id": notice_id,
        "fichier_relatif": relatif,
        "numero_notice": numero,
        "xml_id": notice.get(XML + "id", ""),
        "titre": titre,
        "sous_titre": sous_titre,
        "annees_operation": json.dumps(annees),
        "dates_operation_brutes": " | ".join(annees_brutes),
        "presence_intervalle": "oui" if intervalle else "non",
        "source_annees": source_annees,
        "nombre_ark_terminaux": len({o["ark_terminal"] for o in occurrences}),
        "nombre_occurrences_lieux": len(occurrences),
        "nombre_index_lieux": len(racines),
        "qualite": "a_verifier" if anomalies else "ok",
    }
    return notice_row, occurrences, anomalies


class HashingReader:
    def __init__(self, handle):
        self.handle = handle
        self.sha256 = hashlib.sha256()

    def read(self, taille=-1):
        buffer = self.handle.read(taille)
        self.sha256.update(buffer)
        return buffer


def extraire_fichier(fichier: Path, relatif: str):
    """Parse les notices sans conserver l'arbre XML complet en mémoire."""
    notices, occurrences, anomalies = [], [], []
    with fichier.open("rb") as brut:
        lecteur = HashingReader(brut)
        pile = []
        for event, elem in ET.iterparse(lecteur, events=("start", "end")):
            if event == "start":
                pile.append(elem)
                continue
            if local(elem.tag) == "div" and (
                elem.get("subtype") == "notice" or elem.get("type") == "notice"
            ):
                row, occs, erreurs = extraire_notice(elem, relatif, len(notices) + 1)
                notices.append(row)
                occurrences.extend(occs)
                anomalies.extend(erreurs)
                if len(pile) > 1:
                    pile[-2].remove(elem)
                elem.clear()
            pile.pop()
        sha = lecteur.sha256.hexdigest()
    if not notices:
        anomalies.append({"fichier_relatif": relatif, "type": "aucune_div_notice"})
    return sha, notices, occurrences, anomalies


def alignements_valides(fichier: Path) -> dict[str, dict]:
    """L'unique source utilisable sans nouvel arbitrage est le pilote PACA."""
    data = json.loads(fichier.read_text(encoding="utf-8"))
    if data.get("schema_version") != "0.1.0" or data.get("statut_publication") != "pilote_valide":
        raise ValueError("Pilote Lieux validé non reconnu")
    result = {}
    for autorite in data["autorites"]:
        ark = autorite["ark_pactols"]
        if ark in result:
            raise ValueError("ARK dupliqué dans le pilote : " + ark)
        liens = autorite["correspondances"]
        if len(liens) != 1 or liens[0]["validation"]["statut"] != "VALIDE_EDITEUR_2026_10_18":
            raise ValueError("Alignement non validé : " + ark)
        result[ark] = liens[0]
    if len(result) != 103:
        raise ValueError("Le jeu PACA devrait comprendre 103 autorités")
    return result


def construire_synthese(notices: list[dict], occurrences: list[dict], alignements: dict):
    par_ark = defaultdict(lambda: {"notices": set(), "fichiers": set(), "annees": set(),
                                   "sans_annee": set(), "n": 0, "noms": Counter()})
    for occ in occurrences:
        ark = occ["ark_terminal"]
        a = par_ark[ark]
        a["notices"].add(occ["notice_id"])
        a["fichiers"].add(occ["fichier_relatif"])
        a["annees"].update(json.loads(occ["annees_operation"]))
        if not json.loads(occ["annees_operation"]):
            a["sans_annee"].add(occ["notice_id"])
        a["n"] += 1
        if occ["libelle_terminal_fr"]:
            a["noms"][occ["libelle_terminal_fr"]] += 1
    autorites, lignes_alignement = [], []
    for ark, a in sorted(par_ark.items()):
        label = sorted(a["noms"].items(), key=lambda x: (-x[1], x[0]))[0][0] if a["noms"] else ""
        lien = alignements.get(ark)
        statut = "valide_pilote_paca_2026" if lien else "hors_pilote_non_instruit"
        code = lien["code_insee"] if lien else ""
        nom_cog = lien["libelle_cog"] if lien else ""
        ann = sorted(a["annees"])
        autorites.append({
            "ark_pactols": ark, "libelle_fr_xml": label,
            "nombre_notices_distinctes": len(a["notices"]),
            "nombre_occurrences": a["n"], "nombre_fichiers": len(a["fichiers"]),
            "annees_operation_relevees": json.dumps(ann),
            "premiere_annee_relevee": ann[0] if ann else "",
            "derniere_annee_relevee": ann[-1] if ann else "",
            "notices_sans_annee": len(a["sans_annee"]),
            "alignement_pilote": statut,
            "code_insee_2026_valide": code, "nom_cog_2026_valide": nom_cog,
        })
        lignes_alignement.append({
            "ark_pactols": ark, "libelle_fr_xml": label,
            "nombre_notices_distinctes": len(a["notices"]),
            "statut": statut, "code_insee_2026": code, "nom_cog_2026": nom_cog,
            "source_validation": lien["validation"].get("source", "") if lien else "",
        })
    return autorites, lignes_alignement


def ecrire_csv(path: Path, colonnes: tuple[str, ...], lignes: list[dict]):
    with path.open("w", encoding="utf-8-sig", newline="") as sortie:
        writer = csv.DictWriter(sortie, delimiter=";", fieldnames=colonnes,
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(lignes)


def execution(racine: Path, output_dir: Path, *, pilote: Path, inventaire_seul=False):
    racine = racine.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    if not racine.is_dir():
        raise ValueError("Répertoire XML introuvable : " + str(racine))
    if output_dir == racine or racine in output_dir.parents:
        raise ValueError("La sortie doit être située EN DEHORS du répertoire des XML")
    # Refuser la publication accidentelle sur GitHub Pages.
    depot = Path(__file__).resolve().parents[1]
    if output_dir == depot / "docs" or depot / "docs" in output_dir.parents:
        raise ValueError("Publication directe dans docs interdite")
    fichiers = inventaire(racine)
    retenus = [row for row in fichiers if row["decision"] == "inclu"]
    if not retenus:
        raise ValueError("Aucun fichier XML AdlFI retenu après application des filtres")
    output_dir.mkdir(parents=True, exist_ok=True)
    if inventaire_seul:
        ecrire_csv(output_dir / "inventaire_xml.csv", INV_CSV_FIELDS, fichiers)
        print(f"INVENTAIRE : {len(retenus)} XML retenus sur {len(fichiers)} XML. ")
        print(f"SORTIE : {output_dir / 'inventaire_xml.csv'}")
        return {"inclus": len(retenus), "examines": len(fichiers)}

    alignements = alignements_valides(pilote)
    notices, occurrences, anomalies = [], [], []
    sha_seen = {}
    for i, fichier in enumerate(retenus, 1):
        try:
            sha, n, o, err = extraire_fichier(fichier["path"], fichier["fichier_relatif"])
            fichier["sha256"] = sha
            fichier["notices"] = len(n)
            if sha in sha_seen:
                fichier["decision"] = "doublon"
                fichier["raison"] = "contenu_identique_sha256"
                fichier["erreur"] = "Doublon exact de : " + sha_seen[sha]
                anomalies.append({"fichier_relatif": fichier["fichier_relatif"],
                                  "type": "fichier_identique_sha256",
                                  "autre_fichier": sha_seen[sha]})
                print(f"DOUBLON EXACT IGNORÉ DANS LES STATISTIQUES : "
                      f"{fichier['fichier_relatif']}", flush=True)
                continue
            sha_seen[sha] = fichier["fichier_relatif"]
            notices.extend(n)
            occurrences.extend(o)
            anomalies.extend(err)
            print(f"[{i}/{len(retenus)}] {fichier['fichier_relatif']} : "
                  f"{len(n)} notices, {len(o)} index terminaux", flush=True)
        except (ET.ParseError, OSError, UnicodeError, ValueError) as erreur:
            fichier["decision"] = "erreur"
            fichier["erreur"] = f"{type(erreur).__name__}: {erreur}"
            anomalies.append({"fichier_relatif": fichier["fichier_relatif"],
                              "type": "erreur_lecture_xml", "detail": fichier["erreur"]})
            print(f"ERREUR : {fichier['fichier_relatif']} : {fichier['erreur']}", file=sys.stderr)
    autorites, lignes_alignement = construire_synthese(notices, occurrences, alignements)
    ecrire_csv(output_dir / "inventaire_xml.csv", INV_CSV_FIELDS, fichiers)
    ecrire_csv(output_dir / "notices.csv", MAIN_CSV_FIELDS, notices)
    ecrire_csv(output_dir / "occurrences_lieux.csv", OCC_CSV_FIELDS, occurrences)
    ecrire_csv(output_dir / "autorites_lieux.csv", AUTH_CSV_FIELDS, autorites)
    ecrire_csv(output_dir / "alignements_lieux.csv", ALIGN_CSV_FIELDS, lignes_alignement)
    err_by_type = dict(sorted(Counter(x["type"] for x in anomalies).items()))
    rapport = {
        "schema_version": "0.1.0", "etat": "audit_local_non_publie",
        "source": {"nom_repertoire_source": racine.name,
                   "filtre_nom_inclure": "AdlFI (insensible à la casse)",
                   "filtre_nom_exclure": "Edito/Édito (insensible à la casse et aux accents)",
                   "extension": ".xml", "parcours": "recursif"},
        "effectifs": {
            "fichiers_xml_examines": len(fichiers),
            "fichiers_retenus_par_nom": len(retenus),
            "fichiers_exclus": len(fichiers) - len(retenus),
            "fichiers_xml_en_erreur": sum(f["decision"] == "erreur" for f in fichiers),
            "fichiers_doublons_exacts_exclus_des_statistiques": sum(
                f["decision"] == "doublon" for f in fichiers),
            "fichiers_traites_uniques": sum(f["decision"] == "inclu" for f in fichiers),
            "notices": len(notices),
            "notices_sans_annee": sum(not r["annees_operation"] or r["annees_operation"] == "[]"
                                      for r in notices),
            "notices_sans_index_geographique": sum(int(r["nombre_ark_terminaux"]) == 0 for r in notices),
            "occurrences_terminales": len(occurrences),
            "autorites_distinctes": len(autorites),
            "autorites_alignees_pilote_paca": sum(a["alignement_pilote"] == "valide_pilote_paca_2026" for a in autorites),
            "autorites_hors_pilote": sum(a["alignement_pilote"] == "hors_pilote_non_instruit" for a in autorites),
        },
        "anomalies_par_type": err_by_type,
        "anomalies": anomalies,
        "note": ("Les années relevées ne développent pas automatiquement les intervalles. "
                 "Les identifiants Pactols hiérarchiques ne sont pas multipliés en occurrences. "
                 "Le statut hors_pilote n'est pas un refus de correspondance COG."),
    }
    (output_dir / "rapport_audit.json").write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("BILAN : " + json.dumps(rapport["effectifs"], ensure_ascii=False))
    print("SORTIE (aucune modification des XML) : " + str(output_dir))
    return rapport


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("racine_xml", type=Path, help="Dossier AdlFI_NOTICES-FAITES du sDrive")
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="Dossier de sortie distinct du corpus et de docs/data")
    parser.add_argument("--lieux-json", type=Path, default=Path(__file__).resolve().parents[1]
                        / "docs/data/lieux.json", help="Pilote validé PACA, en lecture seule")
    parser.add_argument("--inventaire-seul", action="store_true",
                        help="Lister seulement les XML retenus/exclus (sans parser les notices)")
    args = parser.parse_args()
    try:
        execution(args.racine_xml, args.output_dir, pilote=args.lieux_json,
                  inventaire_seul=args.inventaire_seul)
    except (ValueError, OSError) as erreur:
        parser.exit(2, f"ERREUR : {erreur}\n")


if __name__ == "__main__":
    main()