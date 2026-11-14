# Référentiel Lieux — périodes officielles des états du lot 001 (COG 2026)

**Date : 14 novembre 2026. Statut : recette non validante ; aucune nouvelle correspondance Pactols–COG publiée.**

## Sources et contrôle reproductible

- Source Insee : [`v_commune_depuis_1943.csv`](https://www.insee.fr/fr/statistiques/fichier/8740222/v_commune_depuis_1943.csv), millésime COG 2026, SHA-256 `08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee`.
- Référence : `docs/lieux/recette/graphe-episodes-cog-lot001.json` (33 états, 11 opérations, 23 arcs).
- Auditeur : `scripts/enrichir_periodes_cog_lot001.py` ; [exécution GitHub Actions réussie](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43594701849).
- Sorties archivées : `graphe-episodes-cog-lot001-dates.json`, `revue-periodes-cog-lot001.csv`, `rapport-periodes-cog-lot001.json`.

**Résultat : 26/26 états `COM` retrouvés dans un couple officiel unique compatible** et **7/7 états `COMD`/`COMA` sans couple historique dans cette source**, conformément à son périmètre. Aucune incompatibilité chronologique, aucune homonymie d’intervalle sur ce lot.

La table source comporte **42 333 lignes distinctes**, dont 42 288 `COM`, 45 `ARM`, et **deux intervalles de durée nulle**. Ceux-ci sont conservés en provenance mais n’attestent aucune période.

## Les 26 états COM datés

| Dossier d’instruction | Type | Code COG | Libellé officiel | Début du couple | Fin exclusive |
|---|---|---|---|---|---|
| Abbéville-la-Rivière | `COM` | `78001` | Abbéville-la-Rivière | 1943-01-01 | 1968-01-01 |
| Abbéville-la-Rivière | `COM` | `91001` | Abbéville-la-Rivière | 1968-01-01 | Actif au 01/01/2026 |
| Afa | `COM` | `20001` | Afa | 1943-01-01 | 1976-01-01 |
| Afa | `COM` | `2A001` | Afa | 1976-01-01 | Actif au 01/01/2026 |
| Aghione | `COM` | `20002` | Aghione | 1943-01-01 | 1976-01-01 |
| Aghione | `COM` | `2B002` | Aghione | 1976-01-01 | Actif au 01/01/2026 |
| Aigondigné | `COM` | `79004` | Aigonnay | 1943-01-01 | 2019-01-01 |
| Aigondigné | `COM` | `79185` | Mougon | 1943-01-01 | 2017-01-01 |
| Aigondigné | `COM` | `79240` | Sainte-Blandine | 1943-01-01 | 2019-01-01 |
| Aigondigné | `COM` | `79327` | Thorigné | 1943-01-01 | 2017-01-01 |
| Aigondigné | `COM` | `79185` | Mougon-Thorigné | 2017-01-01 | 2019-01-01 |
| Aigondigné | `COM` | `79185` | Aigondigné | 2019-01-01 | Actif au 01/01/2026 |
| Alfortville | `COM` | `75001` | Alfortville | 1943-01-01 | 1968-01-01 |
| Alfortville | `COM` | `94002` | Alfortville | 1968-01-01 | Actif au 01/01/2026 |
| Allaines-Mervilliers | `COM` | `28199` | Janville | 1943-01-01 | 2019-01-01 |
| Allaines-Mervilliers | `COM` | `28311` | Le Puiset | 1943-01-01 | 2019-01-01 |
| Allaines-Mervilliers | `COM` | `28002` | Allaines-Mervilliers | 1972-12-28 | 2019-01-01 |
| Allaines-Mervilliers | `COM` | `28199` | Janville-en-Beauce | 2019-01-01 | Actif au 01/01/2026 |
| Antony | `COM` | `75002` | Antony | 1943-01-01 | 1968-01-01 |
| Antony | `COM` | `92002` | Antony | 1968-01-01 | Actif au 01/01/2026 |
| Argenteuil | `COM` | `78018` | Argenteuil | 1943-01-01 | 1968-01-01 |
| Argenteuil | `COM` | `95018` | Argenteuil | 1968-01-01 | Actif au 01/01/2026 |
| Aulnay-sous-Bois | `COM` | `78032` | Aulnay-sous-Bois | 1943-01-01 | 1968-01-01 |
| Aulnay-sous-Bois | `COM` | `93005` | Aulnay-sous-Bois | 1968-01-01 | Actif au 01/01/2026 |
| Colombier-Saugnieu | `COM` | `38119` | Colombier-Saugnieu | 1943-01-01 | 1971-04-01 |
| Colombier-Saugnieu | `COM` | `69299` | Colombier-Saugnieu | 1971-04-01 | Actif au 01/01/2026 |

## Sept états absents de la table des couples code–libellé

Ces absences ne démontrent pas la disparition d’une commune déléguée ou associée : la source historique des couples couvre `COM`/`ARM`. Les événements et le COG des communes existantes doivent être interrogés séparément.

| Dossier | TYPECOM | Code | Libellé | Date d’événement déjà connue |
|---|---|---|---|---|
| Aigondigné | `COMD` | `79004` | Aigonnay | ["2019-01-01"]/[] |
| Aigondigné | `COMD` | `79185` | Mougon | ["2017-01-01"]/[] |
| Aigondigné | `COMD` | `79240` | Sainte-Blandine | ["2019-01-01"]/[] |
| Aigondigné | `COMD` | `79327` | Thorigné | ["2017-01-01"]/[] |
| Allaines-Mervilliers | `COMA` | `28244` | Mervilliers | []/["2019-01-01"] |
| Allaines-Mervilliers | `COMD` | `28002` | Allaines-Mervilliers | ["2019-01-01"]/[] |
| Allaines-Mervilliers | `COMD` | `28199` | Janville | ["2019-01-01"]/[] |

## Garanties et réserves éditoriales

1. Les intervalles sont **[DATE_DEBUT, DATE_FIN[** : la date de fin n’appartient plus à l’épisode du couple.
2. La borne `1943-01-01` correspond souvent au début du **périmètre chronologique de la base** ; il ne faut pas la prendre pour la date de création d’une commune.
3. Une fin vide signifie **actif au COG 2026**, non « sans fin » dans un futur non observé.
4. Une période `COM` date uniquement le **couple code–libellé**, pas la stabilité de l’emprise territoriale. Les `MOD=32` peuvent changer le territoire en conservant un code.
5. Aucun code actuel de commune nouvelle ne devient géométrie de son ancienne commune. Les géométries 2026 demeurent **contemporaines** et ne sont pas des contours historiques.
6. Tous les liens Pactols–COG de ce lot restent **non validés éditorialement** et ne doivent pas être exposés sur GitHub Pages.

## Étape complémentaire

Le script `scripts/auditer_statuts_delegues_associes.py` examine la **présence en 2026** et les **événements de naissance/sortie** des sept `COMD` et `COMA` à partir des fichiers `v_commune_2026.csv` et `v_mvt_commune_2026.csv`. La relation `COMPARENT` n’est attribuée qu’à un état effectivement présent dans le millésime 2026.

## Contrôle complémentaire des sept COMD/COMA — résultats réels

Le fichier des événements **`v_mvt_commune_2026.csv`** (13 734 lignes, SHA-256
`8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1`)
et les communes existantes **`v_commune_2026.csv`** (37 496 lignes, SHA-256
`7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3`)
ont été confrontés aux sept états du graphe.

Contrôle GitHub Actions réussi : https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43595605080

| Type | Code | Entité | Première entrée attestée | Dernière sortie attestée | Au COG 2026 | COMPARENT 2026 |
| --- | --- | --- | --- | --- | --- | --- |
| COMD | `79004` | Aigonnay | 2019-01-01 | — | oui | `79185` |
| COMD | `79185` | Mougon | 2017-01-01 | — | oui | `79185` |
| COMD | `79240` | Sainte-Blandine | 2019-01-01 | — | oui | `79185` |
| COMD | `79327` | Thorigné | 2017-01-01 | — | oui | `79185` |
| COMD | `28002` | Allaines-Mervilliers | 2019-01-01 | — | oui | `28199` |
| COMD | `28199` | Janville | 2019-01-01 | — | oui | `28199` |
| COMA | `28244` | Mervilliers | 1972-12-28 | 2019-01-01 | non | — |

Les états `COMD` présents au COG 2026 sont donc **six sur six** ;
l'ancienne commune associée **Mervilliers** a une disparition de statut
attestée le 1er janvier 2019. **Ces dates sont des événements officiels,
pas des géométries historiques ; la présence au millésime 2026 ne constitue
pas une démonstration de stabilité territoriale.**

Pièces de recette conservées :
- `docs/lieux/recette/rapport-statut-delegue-associe-lot001.json` ;
- `docs/lieux/recette/revue-statut-delegue-associe-lot001.csv` ;
- `docs/lieux/recette/audit-statut-delegue-associe-lot001.json`.

**Bilan global du lot 001 :** 26 états `COM` datés par les couples
officiels ; 6 `COMD` présentes en 2026, avec dates d'entrée
attestées ; 1 `COMA` disparue en 2019 ; **zéro nouvel alignement
Pactols–COG validé** et **zéro géométrie historique attribuée**.
