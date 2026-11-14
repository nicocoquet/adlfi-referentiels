# Pays de la Loire — résultats du lot pilote de 25 ARK (14 novembre 2026)

**Recette non validante, PR n°24.** Exécution GitHub Actions : https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43602311413 — **réussie**.

## Contrôles réalisés sur les fichiers officiels Insee 2026

Les tests synthétiques, le téléchargement Insee, les vérifications SHA-256, l'audit des 25 lignes et l'archivage des résultats ont tous réussi dans le job `audit`.

| Indicateur | Résultat |
| --- | ---: |
| Autorités Pactols du lot | **25** |
| Assertions Pactols vers un code communal Insee | **22** |
| Sans code communal SKOS exploitable | **3** |
| Communes présentes au COG 2026 avec concordance code/région/département | **20** |
| Code partagé entre types administratifs à instruire | **1** |
| Commune associée ou déléguée à instruire | **1** |
| Lignes de périodes historiques rattachées directement aux codes | **25** |
| Lignes d'événements rattachées directement aux codes et répétées par ARK au besoin | **24** |
| Nouveaux alignements AdlFI validés | **0** |
| Géométries historiques attribuées | **0** |

Ces lignes de périodes et de mouvements ne sont **pas** des opérations distinctes, et ne reconstituent pas la généalogie complète des communes : l'auditeur pilote ne traverse pas les événements vers les communes prédécesseures.

## Sources figées (SHA-256)

- `lot-01-pays-de-la-loire.csv` : `1351dacdaeee28e5aa780a886c25692d1ab40be5582c5335472f84ae4c8e6852`
- `v_commune_2026.csv` : `7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3`
- `v_commune_depuis_1943.csv` : `08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee`
- `v_mvt_commune_2026.csv` : `8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1`

Les CSV de contrôle et le rapport complet sont archivés dans l'artefact GitHub Actions `audit-lieux-pays-de-la-loire-lot25`, sans publication dans GitHub Pages.

**Suite :** reconstituer l'inventaire des **806 ARK**, en conservant pour chacun les hiérarchies Pactols et les URI exactMatch de l'export officiel ; ne pas déduire les 781 ARK restants à partir des seuls libellés de `autorites-minimales-9928.json`.
