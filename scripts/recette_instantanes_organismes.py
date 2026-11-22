"""Charger les instantanés JSON publics à leurs commits de publication immuables.

Aucune rétroprojection de l'état courant : les tests de reconstruction historiques
doivent contrôler la version effectivement publiée, et non une estimation.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SNAPSHOTS = {
    "1.55": (
        "dc108f6da0f7d72e9da921a5c40ff6a81420af67",
        "AdlFI_referentiel_1-55_A05C_GAVS_PRETECH_INRAP_CANDIDAT.xlsx",
        "2bd1df994401624fe84c0d696d1ecb1d13266d9b03cadb7ef76e3b65d3ae3c35",
    ),
    "1.56": (
        "c12b1998e76ba777f6cb74e81e1e9c55657dc20a",
        "AdlFI_referentiel_1-56_A05D_GAVS_PRETECH_QUALIFIE_CANDIDAT.xlsx",
        "0410751ceaea8831cac45935afc65dd71b2b187060f0641215c90ad1822ac389",
    ),
    "1.57": (
        "04f3bb57faa9d866b0c307ab186e3f0766222f43",
        "AdlFI_referentiel_1-57_A05E_NANTES_GAVS_QUALIFIE_CANDIDAT.xlsx",
        "8408870084fc5bd2407f75a36cb308e28c220e21d1b3f03a61254bf03a87a009",
    ),
    "1.60": (
        "8dbac1ed2afe0e7a65022da8f332d0338f54bc3b",
        "AdlFI_referentiel_1-60_lot01_quatre_activites_CANDIDAT.xlsx",
        "70aeff4fedc66a54d1a45240af0d22cee1130565e2b29cefb1495e83aa434098",
    ),
    "1.59": (
        "3b34b353f11cc702531de0e83237bcb4c81fac90",
        "AdlFI_referentiel_1-59_activites_CANDIDAT.xlsx",
        "3926b703b9e0fb20d3ed09068282ca97ea718eff14659ba8e3692b2cae0fe53e",
    ),
    "1.58": (
        "d4f3f80a2242774ca193e421aab24e70b3798311",
        "AdlFI_referentiel_1-58_A05F_ARCHEO_ATLANTICA_CANDIDAT.xlsx",
        "6aa15da3019bc0a08987cd48631e95d09172d36b9fb80009b10a9636f1bf67d8",
    ),
}


def charger_instantane(version: str) -> dict:
    commit, filename, sha = SNAPSHOTS[version]
    result = subprocess.run(
        ["git", "show", f"{commit}:docs/data/organismes.json"],
        cwd=ROOT, capture_output=True, check=False,
    )
    if result.returncode:
        raise RuntimeError(
            f"Instantané {version} absent de l'historique local ({commit}). "
            "Récupérer les commits épinglés ; ne pas reconstituer depuis le JSON courant. "
            + result.stderr.decode("utf-8", errors="replace")[:400]
        )
    data = json.loads(result.stdout.decode("utf-8"))
    provenance = data["provenance"]
    if (provenance["source_filename"], provenance["source_sha256"]) != (filename, sha):
        raise AssertionError(f"Provenance de l'instantané {version} incorrecte au commit {commit}")
    return data
