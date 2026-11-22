#!/usr/bin/env python3
"""Parité officielle complète des maîtres privés 1.57 et 1.58 avec leurs PR.

À exécuter depuis une copie du dépôt (la branche courante peut être 1.58) :
  git fetch origin
  python3 scripts/recette_parite_maitres_157_158.py "/chemin/...1-57...xlsx" "/chemin/...1-58...xlsx"

Lecture seule des maîtres et du JSON Git ; n'écrit que le rapport facultatif --report.
Ne pousse aucun XLSX dans GitHub.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EPOCH = "1795305600"
SOURCES = {
    "1.57": {
        "filename": "AdlFI_referentiel_1-57_A05E_NANTES_GAVS_QUALIFIE_CANDIDAT.xlsx",
        "sha256": "8408870084fc5bd2407f75a36cb308e28c220e21d1b3f03a61254bf03a87a009",
        "ref": "refs/remotes/origin/pub/organismes-157-a05e-20261122",
        "counts": (934, 734, 682, 600),
    },
    "1.58": {
        "filename": "AdlFI_referentiel_1-58_A05F_ARCHEO_ATLANTICA_CANDIDAT.xlsx",
        "sha256": "6aa15da3019bc0a08987cd48631e95d09172d36b9fb80009b10a9636f1bf67d8",
        "ref": "refs/remotes/origin/pub/organismes-158-a05f-archeo-atlantica-20261122",
        "counts": (935, 735, 683, 600),
    },
}
OFFICIAL_CODE = (
    "scripts/export_organismes.py",
    "scripts/sector_inheritance.py",
    "scripts/level_inheritance.py",
)


def git_bytes(*args: str) -> bytes:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, check=False
    )
    if result.returncode:
        raise RuntimeError(
            f"git {' '.join(args)} : {result.stderr.decode('utf-8', 'replace').strip()}"
        )
    return result.stdout


def differences(a, b, path="$", limit=25):
    problems = []
    def walk(x, y, at):
        if len(problems) >= limit:
            return
        if type(x) is not type(y):
            problems.append(f"{at}: types {type(x).__name__} / {type(y).__name__}")
        elif isinstance(x, dict):
            for key in sorted(set(x) | set(y)):
                if len(problems) >= limit:
                    return
                if key not in x or key not in y:
                    problems.append(f"{at}.{key}: champ absent")
                else:
                    walk(x[key], y[key], f"{at}.{key}")
        elif isinstance(x, list):
            if len(x) != len(y):
                problems.append(f"{at}: {len(x)} vs {len(y)} entrées")
            for i, (xx, yy) in enumerate(zip(x, y)):
                if len(problems) >= limit:
                    return
                walk(xx, yy, f"{at}[{i}]")
        elif x != y:
            problems.append(f"{at}: {x!r} ≠ {y!r}")
    walk(a, b, path)
    return problems


def verify_one(version: str, source: Path, ref: str, build) -> dict:
    spec = SOURCES[version]
    info = {"version": version, "ref": ref, "master": source.name, "passed": False}
    if not source.is_file():
        raise ValueError(f"maître {version} introuvable : {source}")
    if source.name != spec["filename"]:
        raise ValueError(f"nom de maître {version} : {source.name!r} ; attendu {spec['filename']!r}")
    sha = hashlib.sha256(source.read_bytes()).hexdigest()
    info["master_sha256"] = sha
    if sha != spec["sha256"]:
        raise ValueError(f"empreinte maître {version} incorrecte : {sha}")

    info["commit"] = git_bytes("rev-parse", ref).decode().strip()
    # L'exporteur (et ses deux modules de résolution) doit être identique à la
    # version déposée sur la branche de publication testée.
    for path in OFFICIAL_CODE:
        local = (ROOT / path).read_bytes()
        committed = git_bytes("show", f"{ref}:{path}")
        if local != committed:
            raise ValueError(
                f"{version}: exporteur local différent du commit de la PR : {path}"
            )
    reference = json.loads(git_bytes("show", f"{ref}:docs/data/organismes.json"))
    if reference["provenance"]["source_filename"] != source.name:
        raise ValueError(f"{version}: provenance du JSON de la PR incorrecte")
    if reference["provenance"]["source_sha256"] != sha:
        raise ValueError(f"{version}: SHA du maître différente dans la PR")
    previous = os.environ.get("SOURCE_DATE_EPOCH")
    os.environ["SOURCE_DATE_EPOCH"] = EPOCH
    try:
        computed = build(source)
    finally:
        if previous is None:
            os.environ.pop("SOURCE_DATE_EPOCH", None)
        else:
            os.environ["SOURCE_DATE_EPOCH"] = previous
    problems = differences(computed, reference)
    info["differences"] = problems
    info["counts"] = [
        len(computed["authorities"]),
        computed["totals"]["organismes"],
        computed["totals"]["catalog_included"],
        len(computed["relations"]),
    ]
    if tuple(info["counts"]) != spec["counts"]:
        problems.append(f"{version}: compteurs {info['counts']} au lieu de {spec['counts']}")
    info["passed"] = not problems
    return info


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("master_157", type=Path)
    parser.add_argument("master_158", type=Path)
    parser.add_argument("--ref-157", default=SOURCES["1.57"]["ref"])
    parser.add_argument("--ref-158", default=SOURCES["1.58"]["ref"])
    parser.add_argument("--report", type=Path, help="Rapport JSON facultatif, hors dépôt public")
    args = parser.parse_args(argv)

    # Import après la vérification de l'environnement local.
    sys.path.insert(0, str(ROOT))
    from scripts.export_organismes import build

    results = []
    for version, source, ref in (
        ("1.57", args.master_157, args.ref_157),
        ("1.58", args.master_158, args.ref_158),
    ):
        try:
            result = verify_one(version, source.expanduser().resolve(), ref, build)
        except Exception as exc:
            result = {"version": version, "passed": False, "error": str(exc)}
        results.append(result)
        print(f"PARITÉ {version} : {'OK' if result['passed'] else 'ÉCHEC'}")
        if not result["passed"]:
            for line in result.get("differences", [])[:25]:
                print("  -", line, file=sys.stderr)
            if result.get("error"):
                print("  -", result["error"], file=sys.stderr)
        else:
            print("  commit :", result["commit"])
            print("  maître :", result["master_sha256"])
            print("  effectifs :", result["counts"])

    final = {"source_date_epoch": EPOCH, "results": results,
             "passed": all(result["passed"] for result in results)}
    if args.report:
        args.report.expanduser().resolve().write_text(
            json.dumps(final, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8"
        )
        print("Rapport :", args.report)
    return 0 if final["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
