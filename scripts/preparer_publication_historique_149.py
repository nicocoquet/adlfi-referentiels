#!/usr/bin/env python3
"""Prépare et contrôle un JSON candidat depuis le maître 1.49 sans publier.

Usage : python3 scripts/preparer_publication_historique_149.py /chemin/maitre-1.49.xlsx

La source XLSX privée reste locale. Le JSON candidat est écrit dans le
dossier temporaire du système, jamais directement dans docs/data/.
"""
from __future__ import annotations
import argparse
import json
import tempfile
from pathlib import Path

if __package__:
    from .export_organismes import build
    from .audit_publication_historique_149 import audit, SOURCE_SHA
else:
    from export_organismes import build
    from audit_publication_historique_149 import audit, SOURCE_SHA

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('maitre',type=Path,help='Chemin vers le XLSX privé 1.49')
    parser.add_argument('--destination',type=Path,help='Chemin facultatif du JSON candidat (hors docs/data)')
    args=parser.parse_args()
    xlsx=args.maitre.expanduser().resolve()
    if not xlsx.is_file():
        parser.error(f'Maître introuvable : {xlsx}')
    baseline_path=ROOT/'docs/data/organismes.json'
    if not baseline_path.is_file():
        parser.error(f'JSON publié introuvable : {baseline_path}')
    destination=(args.destination.expanduser() if args.destination else
                 Path(tempfile.gettempdir())/'adlfi-organismes-1-49-candidat.json')
    destination=destination.resolve()
    if destination==baseline_path.resolve():
        parser.error('Refus d’écraser le JSON public avant la recette')
    if destination.suffix.lower()!='.json':
        parser.error('La destination doit être un fichier .json')

    candidate=build(xlsx)
    baseline=json.loads(baseline_path.read_text(encoding='utf-8'))
    result=audit(baseline,candidate,ROOT)
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(candidate,ensure_ascii=False,indent=2),encoding='utf-8')
    print('AUDIT 1.49 OK')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    print('Candidat non publié :',destination)
    print('Source XLSX conservée uniquement sur le poste local.')

if __name__=='__main__':
    main()
