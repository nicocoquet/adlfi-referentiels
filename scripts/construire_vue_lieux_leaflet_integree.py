#!/usr/bin/env python3
"""Construire une recette Leaflet sur les DONNÉES COMMUNALES AdlFI existantes.

La couche administrative 2015–2016 vient du fichier HTML généré et contrôlé
par construire_vue_lieux_multiechelon.py (elle est revalidée ici).
Les chronologies et les contours communaux sont copiés à l'identique depuis
le site statique, pas recalculés ni modifiés. Aucune publication sous docs/.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

REGIONS = ('paca','corse','pdl','bfc')
MARKERS = {'__ADLFI_HISTORICAL_DATA__': 'geo',
           '__ADLFI_COMMUNAL_DATA__': 'communal',
           '__ADLFI_COMMUNAL_CORE__': 'core'}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def historique_depuis_html(path: Path) -> dict:
    texte = path.read_text(encoding='utf-8')
    matches = re.findall(r'<script id="data" type="application/json">(.*?)</script>', texte, flags=re.S)
    if len(matches) != 1:
        raise ValueError('Source administrative contrôlée absente ou multiple')
    data = json.loads(matches[0])
    if (data.get('schema') != 'adlfi.lieux.interface_multiechelon_recette.v1'
        or data.get('alignements_Pactols_generes') != 0
        or data.get('aucune_geometrie_2026_retroprojetee') is not True):
        raise ValueError('Contrat du jeu administratif rompu')
    for annee, nombre in ((2015, (22,96)),(2016,(13,96))):
        capas = data.get('layers', {}).get(str(annee), {})
        if (len(capas.get('region', [])), len(capas.get('departement', []))) != nombre:
            raise ValueError('Cardinalité administrative incorrecte')
        if any(f['properties'].get('annee') != annee or
               f['properties'].get('pactols_valide') is not False
               for niveau in ('region','departement') for f in capas[niveau]):
            raise ValueError('Géographie administrative mal qualifiée')
    return data


def referentiel_communal(dossier: Path, lieux: Path) -> tuple[dict, dict]:
    """Ne modifie aucune valeur source, et conserve les SHA des 9 documents."""
    if not (dossier.is_dir() and lieux.is_file()):
        raise ValueError('Référentiel communal publié introuvable')
    source_paths = {'lieux.json': lieux}
    regions = {}
    for region in REGIONS:
        paths = {'cog': dossier / f'cog-{region}.json',
                 'contours_2026': dossier / f'contours-2026-{region}.geojson'}
        source_paths.update({p.name: p for p in paths.values()})
        cog, contours = (json.loads(paths[key].read_text(encoding='utf-8'))
                         for key in ('cog', 'contours_2026'))
        if (cog.get('region') != region or
            cog.get('schema') != 'adlfi.lieux.chronologie.4regions.public-recette.v1' or
            cog.get('geometries_historiques') != [] or
            contours.get('type') != 'FeatureCollection' or
            contours.get('provenance', {}).get('millesime') != 2026):
            raise ValueError(f'Corpus historique/contours incohérents : {region}')
        liens = cog.get('alignements_Pactols_COG_valides_2026', [])
        if region != 'paca' and liens:
            raise ValueError('Correspondances Pactols hors PACA non autorisées')
        if any(x.get('statut') != 'correspondance_PACA_preexistante_validee'
               or x.get('millesime_validation') != 2026 for x in liens):
            raise ValueError('Correspondance Pactols sans validation éditoriale')
        regions[region] = {'cog': cog, 'contours_2026': contours}
    pactols = json.loads(lieux.read_text(encoding='utf-8'))
    if (pactols.get('schema_version') != '0.1.0' or
        pactols.get('totaux', {}).get('autorites_pactols') != 103 or
        len(pactols.get('autorites', [])) != 103):
        raise ValueError('Les 103 identités du pilote Pactols PACA ont changé')
    return ({'schema': 'adlfi.lieux.integration_communes_recette.v1',
             'regions': regions, 'pactols': pactols},
            {str(k): sha(v) for k,v in sorted(source_paths.items())})


def generer(modele: Path, source_html: Path, dossier: Path,
            lieux: Path, core: Path, sortie: Path) -> dict:
    if 'docs' in sortie.resolve().parts:
        raise ValueError('Interdiction de publier la recette sous docs/')
    origine = historique_depuis_html(source_html)
    communes, empreintes = referentiel_communal(dossier, lieux)
    code = core.read_text(encoding='utf-8')
    if 'AdlfiLieuxChronologieCore' not in code or '</script' in code.lower():
        raise ValueError('Core communal absent ou non sûr à intégrer')
    template = modele.read_text(encoding='utf-8')
    for placeholder in MARKERS:
        if template.count(placeholder) != 1:
            raise ValueError('Balise du modèle manquante ou dupliquée : '+placeholder)
    data = {
        '__ADLFI_HISTORICAL_DATA__': json.dumps(origine, ensure_ascii=False,
              separators=(',', ':'), sort_keys=True).replace('<','\\u003c'),
        '__ADLFI_COMMUNAL_DATA__': json.dumps(communes, ensure_ascii=False,
              separators=(',', ':'), sort_keys=True).replace('<','\\u003c'),
        '__ADLFI_COMMUNAL_CORE__': code,
    }
    for placeholder, contenu in data.items():
        template = template.replace(placeholder, contenu)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(template, encoding='utf-8')
    rapport = {
        'schema': 'adlfi.lieux.recette_integration_leaflet.v1',
        'html': sortie.name,
        'sha256_html': sha(sortie),
        'taille_octets': sortie.stat().st_size,
        'source_administrative_html_sha256': sha(source_html),
        'sources_communales_SHA256': empreintes,
        'autorites_pactols_PACA_intactes': 103,
        'regions_2015':22,'regions_2016':13,
        'departements_2015':96,'departements_2016':96,
        'regions_communales_historiques_reutilisees': list(REGIONS),
        'nouvelles_correspondances_Pactols': 0,
        'fichiers_publics_modifies': 0,
        'publication_docs': False,
    }
    (sortie.parent/'rapport-integration-leaflet.json').write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    return rapport


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for arg in ('modele','source-html','dossier-communautes','lieux','core','sortie'):
        parser.add_argument('--'+arg, required=True,type=Path)
    a=parser.parse_args()
    print(json.dumps(generer(a.modele,a.source_html,a.dossier_communautes,a.lieux,a.core,a.sortie),ensure_ascii=False,indent=2))