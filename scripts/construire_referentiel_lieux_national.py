#!/usr/bin/env python3
"""Prépare le référentiel national des lieux AdlFI, sans publier d'alignements inférés.

Entrées : CSV de l'extracteur XML AdlFI, plus (facultativement) le COG historique
2026 officiel de l'Insee (couples code–libellé depuis 1943). Une correspondance
sur un libellé reste TOUJOURS une candidature, jamais une validation éditoriale.

Python standard uniquement. Les sources sont lues sans modification.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
import re
import unicodedata
from pathlib import Path

ARK_PATTERN = re.compile(r'^26678/[A-Za-z0-9]+$')
HEAD_AUTORITES = {'ark_pactols', 'libelle_fr_xml', 'annees_operation_relevees',
                 'alignement_pilote', 'code_insee_2026_valide'}
HEAD_OCCURRENCES = {'ark_terminal', 'chaine_ark', 'chaine_libelles_fr',
                    'libelle_terminal_fr', 'notice_id'}
HEAD_HISTORIQUE = {'TYPECOM', 'COM', 'LIBELLE', 'DATE_DEBUT', 'DATE_FIN'}
HEAD_ALIGNEMENTS = {'ark_pactols', 'statut', 'code_insee_2026'}


def lire_csv(path: Path, required: set[str]):
    with path.open('r', encoding='utf-8-sig', newline='') as fh:
        peek = fh.read(4096)
        fh.seek(0)
        sep = ';' if peek.split('\n', 1)[0].count(';') > peek.split('\n', 1)[0].count(',') else ','
        reader = csv.DictReader(fh, delimiter=sep)
        fields = set(reader.fieldnames or [])
        if not required <= fields:
            raise ValueError(f'Colonnes manquantes dans {path}: {sorted(required-fields)}')
        for row in reader:
            yield row


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def normaliser(value: str) -> str:
    value = unicodedata.normalize('NFKD', (value or '').replace('œ', 'oe').replace('Œ', 'Oe'))
    value = ''.join(x for x in value if unicodedata.category(x) != 'Mn').casefold()
    return ' '.join(re.sub(r'[^a-z0-9]+', ' ', value).split())


def chemin_francais(chain: list[str]) -> bool:
    return any(x in ('France', 'France métropolitaine', "France d'outre-mer") for x in chain)


def typer(chemins: list[dict]) -> str:
    parts = [p['libelles'] for p in chemins]
    if any(len(x) >= 2 and x[-2].startswith(('Département de ', 'Département du ',
                                            'Département des ', 'Département d\''))
           for x in parts):
        return 'sous_departement_candidat_communal'
    if any(chemin_francais(x) and any(y.startswith('Département ') for y in x) for x in parts):
        return 'sous_commune_ou_lieu_imbrique_a_qualifier'
    if any(chemin_francais(x) for x in parts):
        return 'autre_geographie_francaise_a_qualifier'
    if any(x and x[0] == 'Europe hydrographie' for x in parts):
        return 'hydrographie_hors_cog_communal'
    if any(x and x[0] == 'Europe physique' for x in parts):
        return 'geographie_physique_hors_cog_communal'
    return 'autre_hors_champ_cog_communal'


def lire_annees(value: str) -> tuple[list[int], list[str]]:
    if not value:
        return [], []
    raw = json.loads(value)
    if not isinstance(raw, list):
        raise ValueError('annees_operation_relevees doit être une liste JSON')
    good, anomaly = set(), []
    for x in raw:
        try:
            year = int(x)
        except (ValueError, TypeError):
            anomaly.append(str(x))
            continue
        if 1800 <= year <= 2100:
            good.add(year)
        else:
            anomaly.append(str(x))
    return sorted(good), sorted(set(anomaly))


def lire_historique(path: Path | None) -> dict[str, list[dict]]:
    index = collections.defaultdict(list)
    if not path:
        return index
    for r in lire_csv(path, HEAD_HISTORIQUE):
        if r['TYPECOM'].strip() != 'COM':
            continue  # les ARM, COMA et COMD sont des entités différentes
        code = r['COM'].strip()
        libelle = r['LIBELLE'].strip()
        if not re.fullmatch(r'[0-9A-Z]{5}', code) or not libelle:
            continue
        index[normaliser(libelle)].append({
            'code_insee_historique': code,
            'libelle_cog': libelle,
            'date_debut': r['DATE_DEBUT'].strip(),
            'date_fin': r['DATE_FIN'].strip(),
            'typecom': 'COM',
        })
    for v in index.values():
        v.sort(key=lambda r: (r['code_insee_historique'], r['date_debut'], r['date_fin']))
    return index


def annees_par_rapport_periode(annees: list[int], debut: str, fin: str) -> str:
    """Indicateur indicatif : jamais une preuve de validité d'un nom Pactols.

    Les bornes Insee sont prises par convention [DATE_DEBUT, DATE_FIN[ ;
    les années sont des plages calendaires, non des dates ponctuelles.
    """
    if not annees:
        return 'sans_annee_operation'
    if not debut:
        return 'periode_incomplete'
    try:
        debut_year = int(debut[:4]); fin_year = int(fin[:4]) if fin else 10000
    except ValueError:
        return 'periode_invalide'
    ok = any(a >= debut_year and (not fin or a <= fin_year) for a in annees)
    return 'chevauchement_annuel_possible' if ok else 'annees_hors_periode_libelle'


def construire(autorites_csv: Path, occurrences_csv: Path, alignements_csv: Path,
               out: Path, cog_historique: Path | None = None) -> dict:
    sources = {'autorites_xml': autorites_csv, 'occurrences_xml': occurrences_csv,
               'alignements_pilote': alignements_csv}
    if cog_historique:
        sources['cog_historique_insee_2026'] = cog_historique
    for label, source in sources.items():
        if not source.is_file():
            raise FileNotFoundError(f'Source absente ({label}): {source}')
    # Ne jamais confondre dossier d'entrée et dossier d'export : seules des
    # cibles de sortie entièrement distinctes sont admises.
    dests = [out / x for x in ('autorites_nationales.json', 'candidatures_cog_historiques.csv',
                              'rapport_preparation.json')]
    if any(x.resolve() in {p.resolve() for p in sources.values()} for x in dests):
        raise ValueError('Une cible de sortie écraserait un fichier source')

    csv_autorites = list(lire_csv(autorites_csv, HEAD_AUTORITES))
    by_ark = {r['ark_pactols']: r for r in csv_autorites}
    if len(by_ark) != len(csv_autorites) or any(not ARK_PATTERN.fullmatch(k) for k in by_ark):
        raise ValueError('ARK vide, mal formé ou dupliqué dans les autorités XML')
    chemins = collections.defaultdict(dict)
    variantes = collections.defaultdict(set)
    attestations = {}
    for occ in lire_csv(occurrences_csv, HEAD_OCCURRENCES):
        ark = occ['ark_terminal']
        if ark not in by_ark:
            raise ValueError(f'ARK terminal absent de la table des autorités : {ark}')
        ars = json.loads(occ['chaine_ark'])
        labels = json.loads(occ['chaine_libelles_fr'])
        if not isinstance(ars, list) or not isinstance(labels, list) or len(ars) != len(labels):
            raise ValueError(f'Hiérarchie invalide pour {ark}')
        if ars and ars[-1] != ark:
            raise ValueError(f'Dernier ARK de la chaîne incohérent pour {ark}')
        key = json.dumps([ars, labels], ensure_ascii=False, separators=(',', ':'))
        chemins[ark][key] = {'arks': ars, 'libelles': labels}
        if occ['libelle_terminal_fr'].strip():
            variantes[ark].add(occ['libelle_terminal_fr'].strip())
        attestations.setdefault(ark, {
            'notice_id': occ['notice_id'],
            'fichier_relatif': occ.get('fichier_relatif', ''),
        })
    if set(chemins) != set(by_ark):
        raise ValueError(f'Autorités sans attestation : {len(set(by_ark)-set(chemins))}')

    validated = {}
    for row in lire_csv(alignements_csv, HEAD_ALIGNEMENTS):
        if row['statut'] != 'valide_pilote_paca_2026':
            continue
        a, c = row['ark_pactols'].strip(), row['code_insee_2026'].strip()
        if a not in by_ark or not re.fullmatch(r'[0-9A-Z]{5}', c):
            raise ValueError(f'Alignement historique pilote incohérent : {a} / {c}')
        if a in validated and validated[a] != c:
            raise ValueError(f'Alignements concurrents pour {a}')
        validated[a] = c
    idx = lire_historique(cog_historique)

    results = []
    proposals = []
    report_types = collections.Counter()
    report_status = collections.Counter()
    report_year_errors = []
    chemins_multiples = 0
    chemins_multiples_ark_seuls = 0
    for ark, source in sorted(by_ark.items()):
        paths = sorted(chemins[ark].values(), key=lambda c: json.dumps(c, ensure_ascii=False, sort_keys=True))
        if len(paths) > 1:
            chemins_multiples += 1
        if len({tuple(p['arks']) for p in paths}) > 1:
            chemins_multiples_ark_seuls += 1
        label = source['libelle_fr_xml'].strip()
        names = sorted(variantes[ark] | ({label} if label else set()), key=lambda x: (normaliser(x), x))
        typ = typer(paths)
        years, invalid_years = lire_annees(source['annees_operation_relevees'])
        if invalid_years:
            report_year_errors.append({'ark': ark, 'valeurs': invalid_years})
        found = {}
        if cog_historique and typ not in ('hydrographie_hors_cog_communal',
                                          'geographie_physique_hors_cog_communal',
                                          'autre_hors_champ_cog_communal'):
            for name in names:
                for match in idx.get(normaliser(name), []):
                    ident = (match['code_insee_historique'], match['libelle_cog'],
                             match['date_debut'], match['date_fin'])
                    found[ident] = match
        proposals_for_ark = list(found.values())
        codes = sorted({x['code_insee_historique'] for x in proposals_for_ark})
        if ark in validated:
            status = 'validation_editoriale_paca_2026'
        elif typ.endswith('_hors_cog_communal'):
            status = 'hors_champ_communal_a_qualifier'
        elif not cog_historique:
            status = 'historique_cog_non_fourni'
        elif len(codes) == 1:
            status = 'candidature_lexicale_un_code_a_instruire'
        elif len(codes) > 1:
            status = 'homonymie_plusieurs_codes_a_instruire'
        else:
            status = 'aucune_candidature_lexicale'
        report_types[typ] += 1
        report_status[status] += 1
        results.append({
            'ark_pactols': ark,
            'libelle_documentaire': label,
            'variantes_documentaires': names,
            'hierarchies_pactols_attestees': paths,
            'profil_geographique_provisoire': typ,
            'annees_operation_attestees': years,
            'annees_operation_invalides': invalid_years,
            'attestation_temoin': attestations[ark],
            'validation_existante': ({'nature': 'alignement_editorial_pactols_cog_2026',
                                     'code_insee': validated[ark],
                                     'provenance': 'pilote_PACA_2026'}
                                    if ark in validated else None),
            'statut_raccordement': status,
            'codes_cog_candidats': codes,
            'geometrie': ({'etat': 'geometrie_cog_2026_pilote', 'code_insee': validated[ark],
                            'note': 'contour contemporain, pas historique'}
                          if ark in validated else {'etat': 'aucune_geometrie_validee'}),
        })
        for match in proposals_for_ark:
            proposals.append({
                'ark_pactols': ark, 'libelle_documentaire': label,
                **match,
                'annees_operation_vs_forme_cog': annees_par_rapport_periode(
                    years, match['date_debut'], match['date_fin']),
                'validation_editoriale': 'non_validee',
                'origine': 'egalite_lexicale_exacte_apres_normalisation',
            })

    out.mkdir(parents=True, exist_ok=True)
    catalog = {name: {'fichier': path.name, 'sha256': sha256(path)}
               for name, path in sorted(sources.items())}
    master = {'schema_version': '0.1.0', 'module': 'lieux',
              'statut_publication': 'recette_non_publiee',
              'unite': 'concept_pactols_atteste_dans_XML',
              'avertissement': 'Les années d’opération ne datent pas les délimitations ni les noms administratifs.',
              'sources': catalog, 'autorites': results}
    dests[0].write_text(json.dumps(master, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    pheads = ['ark_pactols', 'libelle_documentaire', 'code_insee_historique',
              'libelle_cog', 'date_debut', 'date_fin', 'typecom',
              'annees_operation_vs_forme_cog', 'validation_editoriale', 'origine']
    with dests[1].open('w', encoding='utf-8-sig', newline='') as fh:
        writer = csv.DictWriter(fh, delimiter=';', fieldnames=pheads)
        writer.writeheader()
        writer.writerows(sorted(proposals, key=lambda x:
                                (x['ark_pactols'], x['code_insee_historique'], x['date_debut'])))
    report = {
        'schema_version': '0.1.0', 'etat': 'recette_non_publiee',
        'nombre_autorites': len(results),
        'nombre_alignees_paca_2026': len(validated),
        'nombre_autorites_a_plusieurs_hierarchies_ark_et_libelles': chemins_multiples,
        'nombre_autorites_a_plusieurs_chemins_ark': chemins_multiples_ark_seuls,
        'nombre_lignes_candidatures_historiques': len(proposals),
        'nombre_annees_invalides_ark': len(report_year_errors),
        'annees_invalides': report_year_errors,
        'repartition_profils': dict(sorted(report_types.items())),
        'repartition_statuts': dict(sorted(report_status.items())),
        'sources': catalog,
        'note_historicite': 'Le fichier COG depuis 1943 fournit les périodes code–libellé ; les mouvements et la succession géométrique restent à instruire séparément.',
    }
    dests[2].write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    return report


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--autorites', type=Path, required=True)
    cli.add_argument('--occurrences', type=Path, required=True)
    cli.add_argument('--alignements', type=Path, required=True)
    cli.add_argument('--cog-historique', type=Path, default=None,
                     help='v_commune_depuis_1943.csv du COG 2026 officiel (facultatif)')
    cli.add_argument('--sortie', type=Path, required=True)
    args = cli.parse_args()
    report = construire(args.autorites,args.occurrences,args.alignements,args.sortie,args.cog_historique)
    print(json.dumps({k:v for k,v in report.items() if k != 'sources' and k != 'annees_invalides'},
                     ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()