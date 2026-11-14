# Lieux — noyau COG temporel national (hors publication)

Cette brique a été extraite de la PR #24 pour permettre sa validation et sa fusion **sans diffuser les dossiers de candidats historiques de cette PR**.

## Périmètre

- Sources : **COG 2026 officiel de l'Insee** : `v_commune_2026.csv`, `v_commune_depuis_1943.csv`, `v_mvt_commune_2026.csv`.
- Acquisition : `scripts/recuperer_cog_2026.py`, avec contrôle obligatoire des trois SHA-256 du jeu déjà audité.
- Génération : `scripts/preparer_index_cog_national_temporel.py`.
- Test unitaire : `tests/test_preparer_index_cog_national_temporel.py`.
- CI autonome : `.github/workflows/lieux-cog-temporel-national.yml`.

Le traitement produit **98 segments JSON de recette** par préfixe de code et un index des noms administratifs historiques. Le préfixe d'un code historique **ne prouve pas l'appartenance à un département actuel ou passé**. Pour les mouvements entre préfixes, la même ligne COG peut figurer dans deux segments ; elle porte un identifiant stable et n'est comptée qu'une fois dans le total national.

| Mesure vérifiée | Nombre |
| --- | ---: |
| Codes ayant eu un statut COM depuis 1943 | 39 117 |
| Périodes de communes COM | 42 288 |
| Arrondissements municipaux ARM actuels | 45 |
| Communes COM actuelles | 34 875 |
| Communes déléguées COMD actuelles | 2 105 |
| Communes associées COMA actuelles | 471 |
| Mouvements officiels uniques | 13 734 |
| Segments JSON | 98 |

## Convention temporelle

Le curseur du module Lieux représente **le 1er janvier de l'année choisie**, entre 1943 et 2026. L'état COM/ARM à cette date est actif si `DATE_DEBUT <= AAAA-01-01 < DATE_FIN`, avec une fin absente assimilée à une ouverture d'intervalle.

Les **deux lignes de durée nulle** du COG sont conservées (Freigné, `44225`, et Pont-Farcy, `50649`) mais ne sont jamais affichées comme un état actif. Les **127 mouvements sans commune antérieure** et les **deux mouvements sans commune postérieure** sont conservés avec leur extrémité vide officielle.

Les fichiers historiques de l'Insee ne permettent pas de reconstituer rétroactivement toutes les périodes de **commune associée ou déléguée**. Ces deux statuts sont présentés comme **observations 2026**, et non extrapolés aux années anciennes.

## Garde-fous de publication

Ce noyau **ne contient aucun ARK Pactols, aucune nouvelle équivalence Pactols–Insee, aucune géométrie historique et aucune décision éditoriale**. Il ne modifie pas les fichiers publics de `docs/data`, ni la page `docs/lieux/index.html`.

Les JSON produits par CI restent un **artefact de recette** (durée de conservation limitée), et ne deviennent **pas automatiquement accessibles dans GitHub Pages**. Les deux sources Pactols (index documentaire et alignements validés PACA) seront raccordées dans une PR de publication distincte, après qualification des liens.

La PR #24 conserve la recherche historique et les dossiers régionaux encore soumis à validation. Le présent lot technique n'autorise pas la fusion de #24.

## Exécution

```bash
python3 -m unittest discover -s tests -p test_preparer_index_cog_national_temporel.py -v

python3 scripts/recuperer_cog_2026.py --sortie /tmp/adlfi-cog-2026

python3 scripts/preparer_index_cog_national_temporel.py \
  --historique /tmp/adlfi-cog-2026/v_commune_depuis_1943.csv \
  --courant /tmp/adlfi-cog-2026/v_commune_2026.csv \
  --mouvements /tmp/adlfi-cog-2026/v_mvt_commune_2026.csv \
  --sortie /tmp/adlfi-lieux-temporel
```
