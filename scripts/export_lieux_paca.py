#!/usr/bin/env python3
"""Export contrôlé du pilote Lieux PACA (Pactols–COG 2026).

Lecture seule des deux sources du dépôt privé atlas-documentaire.
Ne produit que les 103 alignements explicitement validés par l'éditeur.
Aucun rapprochement lexical ne crée de validation, aucun XLSX/CSV source
n'est copié dans le dépôt public Référentiels AdlFI.

Exemple :
    python3 scripts/export_lieux_paca.py \
      /chemin/vers/autorite_pactols_insee.csv \
      /chemin/vers/communes-1000m.geojson \
      --output-dir /tmp/adlfi-lieux-paca-recette
"""
import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path

SOURCE_REPO = "nicocoquet/atlas-documentaire"
SOURCE_COMMIT = "bc0455c7d1dbf65f579e9b25a01eb7928a8054d5"
SOURCE_CSV = "experimentation/donnees/autorite_pactols_insee.csv"
SOURCE_GEO = "cartographie/geometries/communes-1000m.geojson"
SOURCE_CSV_BLOB = "8d039fe574413df89524b39540ba962ce89ca0a0"
SOURCE_GEO_BLOB = "0525607f277ec4c915a3e3273e716a5b1f1108d5"

STATUS_VALID = "VALIDE_EDITEUR_2026_10_18"
STATUS_EXCLUDED = {
    "REVU_EDITEUR_A_DOCUMENTER": 110,
    "HORS_COG_CONFIRME": 3,
    "A_COMPLETER_SOURCE": 2,
}
PACA_DEPS = {"04", "05", "06", "13", "83", "84"}
ARK_PATTERN = re.compile(r"^26678/[A-Za-z0-9]+$")
CODE_PATTERN = re.compile(r"^[0-9]{5}$")
REQUIRED_COLUMNS = {
    "ark_pactols", "libelle_pactols", "type_entite",
    "code_cog_propose", "libelle_cog_propose", "code_cog_valide",
    "statut_validation", "relation", "source_controle", "millesime_cog",
}


def git_blob_sha(raw):
    """Calculer l'identifiant Git exact des octets, y compris le BOM éventuel."""
    header = b"blob " + str(len(raw)).encode("ascii") + b"\0"
    return hashlib.sha1(header + raw).hexdigest()


def _source_provenance(path, sha):
    return {
        "depot": SOURCE_REPO,
        "commit": SOURCE_COMMIT,
        "chemin": path,
        "git_blob_sha": sha,
    }


def construire(csv_bytes, geo_bytes, *, verification_sources=True,
               effectif_attendu=103):
    """Construire les deux publications entièrement en mémoire.

    effectif_attendu est paramétrable pour tester les refus sur corpus synthétique ;
    le programme en ligne de commande exige toujours les 103 validations.
    """
    if verification_sources:
        for name, raw, sha in (
            ("autorités Pactols–COG", csv_bytes, SOURCE_CSV_BLOB),
            ("géométries PACA", geo_bytes, SOURCE_GEO_BLOB),
        ):
            if git_blob_sha(raw) != sha:
                raise ValueError(f"Source {name} différente du blob Git validé")

    source = io.StringIO(csv_bytes.decode("utf-8-sig"), newline="")
    reader = csv.DictReader(source, delimiter=";")
    missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
    if missing:
        raise ValueError("Colonnes éditoriales absentes : " + ", ".join(sorted(missing)))
    lignes = list(reader)
    if not lignes:
        raise ValueError("Corpus éditorial vide")

    statuts = Counter(ligne["statut_validation"] for ligne in lignes)
    inattendus = set(statuts) - {STATUS_VALID, *STATUS_EXCLUDED}
    if inattendus:
        raise ValueError("Statuts éditoriaux inconnus : " + ", ".join(sorted(inattendus)))

    validees = [ligne for ligne in lignes if ligne["statut_validation"] == STATUS_VALID]
    if len(validees) != effectif_attendu:
        raise ValueError(
            f"Effectif validé : {len(validees)} au lieu de {effectif_attendu}"
        )
    if effectif_attendu == 103:
        for statut, attendu in STATUS_EXCLUDED.items():
            if statuts[statut] != attendu:
                raise ValueError(f"Effectif {statut} : {statuts[statut]} au lieu de {attendu}")
        if len(lignes) != 218:
            raise ValueError(f"218 concepts attendus, {len(lignes)} trouvés")

    geo_source = json.loads(geo_bytes.decode("utf-8-sig"))
    if (geo_source.get("type") != "FeatureCollection"
            or not isinstance(geo_source.get("features"), list)):
        raise ValueError("Source géométrique non conforme à GeoJSON FeatureCollection")

    geometries = {}
    for feature in geo_source["features"]:
        if feature.get("type") != "Feature" or not isinstance(feature.get("properties"), dict):
            raise ValueError("Feature GeoJSON invalide")
        code = str(feature["properties"].get("code", ""))
        if not CODE_PATTERN.fullmatch(code) or code in geometries:
            raise ValueError(f"Code géométrique invalide ou dupliqué : {code}")
        if feature.get("geometry", {}).get("type") not in {"Polygon", "MultiPolygon"}:
            raise ValueError(f"Géométrie communale invalide : {code}")
        if not feature["geometry"].get("coordinates"):
            raise ValueError(f"Coordonnées absentes : {code}")
        geometries[code] = feature

    arks, codes, notices = set(), set(), []
    correspondances = {}
    for ligne in validees:
        ark = ligne["ark_pactols"].strip()
        code = ligne["code_cog_valide"].strip()
        if not ARK_PATTERN.fullmatch(ark) or ark in arks:
            raise ValueError(f"ARK Pactols invalide ou dupliqué : {ark}")
        if not CODE_PATTERN.fullmatch(code) or code in codes:
            raise ValueError(f"Code COG validé invalide ou dupliqué : {code}")
        if ligne["code_cog_propose"].strip() != code:
            raise ValueError(f"Code proposé différent du code validé : {ark}")
        if (ligne["type_entite"] != "commune"
                or ligne["relation"] != "correspondance_communale_validee"
                or ligne["millesime_cog"] != "2026"):
            raise ValueError(f"Qualification éditoriale incohérente : {ark}")
        if not all(ligne[k].strip() for k in ("libelle_pactols", "libelle_cog_propose",
                                              "source_controle")):
            raise ValueError(f"Libellé ou provenance manquant : {ark}")
        if code not in geometries:
            raise ValueError(f"Géométrie absente pour code validé {code} ({ark})")
        props = geometries[code]["properties"]
        departement = str(props.get("departement", ""))
        if departement not in PACA_DEPS or str(props.get("region")) != "93":
            raise ValueError(f"Géométrie hors PACA ou mal attribuée : {code}")

        arks.add(ark)
        codes.add(code)
        correspondances[code] = ark
        notices.append({
            "ark_pactols": ark,
            "libelle_pactols": ligne["libelle_pactols"].strip(),
            "type_entite": "commune",
            "correspondances": [{
                "referentiel": "COG",
                "code_insee": code,
                "libelle_cog": ligne["libelle_cog_propose"].strip(),
                "millesime_cog": 2026,
                "departement": departement,
                "region": "93",
                "relation_editoriale": "correspondance_communale_validee",
                "validation": {
                    "statut": STATUS_VALID,
                    "date": "2026-10-18",
                    "source": ligne["source_controle"].strip(),
                },
            }],
        })
    notices.sort(key=lambda n: (n["libelle_pactols"].casefold(), n["ark_pactols"]))

    source_info = {
        "autorites": _source_provenance(SOURCE_CSV, SOURCE_CSV_BLOB),
        "geometries": _source_provenance(SOURCE_GEO, SOURCE_GEO_BLOB),
        "millesime_cog": 2026,
        "validation_editoriale": "2026-10-18",
    }
    lieux = {
        "schema_version": "0.1.0",
        "module": "lieux",
        "perimetre": "PACA",
        "statut_publication": "pilote_valide",
        "provenance": source_info,
        "totaux": {
            "autorites_pactols": len(notices),
            "communes_cog": len(codes),
            "geometries": len(codes),
            "lignes_source": len(lignes),
            "lignes_non_validees_exclues": len(lignes) - len(notices),
        },
        "autorites": notices,
    }
    output_features = []
    for code in sorted(codes):
        original = geometries[code]
        output_features.append({
            "type": "Feature",
            "properties": {
                **original["properties"],
                "ark_pactols": correspondances[code],
            },
            "geometry": original["geometry"],
        })
    geom = {
        "type": "FeatureCollection",
        "metadata": {
            "schema_version": "0.1.0",
            "perimetre": "PACA",
            "millesime_cog": 2026,
            "source": _source_provenance(SOURCE_GEO, SOURCE_GEO_BLOB),
            "source_cartographique": "Contours administratifs 2026 (data.gouv.fr)",
            "url_source_cartographique": "https://www.data.gouv.fr/datasets/contours-administratifs",
            "licence_source": "ODbL-1.0",
            "attribution_source": "Contours administratifs — data.gouv.fr / IGN et contributeurs OpenStreetMap",
            "avertissement": (
                "Les contours sont ceux du fichier cartographique source ; "
                "ils ne représentent pas les limites historiques des communes."
            ),
        },
        "features": output_features,
    }
    if {x["properties"]["code"] for x in geom["features"]} != codes:
        raise AssertionError("Discordance entre autorités et géométries")
    return lieux, geom


def serialiser(data, *, compact=False):
    if compact:
        return json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("autorites", type=Path, help="CSV éditorial Pactols–COG")
    parser.add_argument("geometries", type=Path, help="GeoJSON communal PACA")
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="Dossier de recette explicite (éviter docs/data avant validation)")
    args = parser.parse_args()
    output = args.output_dir.expanduser().resolve()
    if output == (Path(__file__).resolve().parents[1] / "docs/data").resolve():
        parser.error("Écriture directe dans docs/data interdite pendant la recette")
    lieux, geom = construire(args.autorites.read_bytes(), args.geometries.read_bytes())
    output.mkdir(parents=True, exist_ok=True)
    (output / "lieux.json").write_text(serialiser(lieux), encoding="utf-8")
    (output / "lieux-communes.geojson").write_text(serialiser(geom, compact=True), encoding="utf-8")
    print(f"EXPORT LIEUX PACA OK : {len(lieux['autorites'])} autorités, "
          f"{len(geom['features'])} géométries, "
          f"{lieux['totaux']['lignes_non_validees_exclues']} lignes exclues")
    print(f"Candidat non publié : {output}")


if __name__ == "__main__":
    main()
