# Comparaison des régions métropolitaines : états COG et contours SIG 2016 / 2026

**16 novembre 2026 · recette scientifique, non publiée · PR #36**

## Conclusion

Les **13 codes régionaux métropolitains** identifiés dans les millésimes COG **2016 et 2026** sont identiques. La relation **département → région** demeure également identique pour les **101 départements**, soit **zéro changement de rattachement entre les deux instantanés COG** (voir `scripts/auditer_cog_regions_millesimes.py` et sa CI dédiée).

**Il n'en découle pas une égalité des contours géométriques.** La comparaison porte sur des jeux de producteurs, de niveaux de généralisation et de dates distincts ; ses écarts spatiaux ne sont **pas**, à eux seuls, la preuve de changements de frontières administratives.

## Sources comparées

1. **2016** — IGN GEOFLA, archive métropolitaine `GEOFLA_2-2_DEPARTEMENT_SHP_LAMB93_FXX_2016-06-28`, régions obtenues par union de départements de cette même édition, puis transformation WGS 84. États du COG au **01/01/2016**. Aucune géométrie 2026 utilisée.
2. **2026** — GeoJSON 100 m « régions », édition diffusée **04/05/2026** par data.gouv.fr sur la base d'Admin Express IGN ; états du COG au **01/01/2026**. Les collectivités non régionales sont exclues de cette comparaison.
3. Comparaison des géométries en **EPSG:2154 (Lambert-93)**, par code régional. Intersection sur union (IoU) et différence symétrique surfacique. Lorsque la source présente une auto-intersection, un `make_valid` est appliqué **uniquement à la copie de travail SIG**, sans modification des originaux.

## Résultats numériques — échantillon métropolitain exhaustif

| Code | IoU (%) | Différence symétrique (km²) |
|---|---:|---:|
| 11 | 99,7170 | 34,19 |
| 24 | 99,8490 | 59,66 |
| 27 | 99,8641 | 65,27 |
| 28 | 99,7307 | 81,19 |
| 32 | 99,7583 | 77,47 |
| 44 | 99,8642 | 78,41 |
| 52 | 99,7678 | 75,23 |
| 53 | 99,3945 | 166,49 |
| 75 | 99,8467 | 130,57 |
| 76 | 99,8705 | 95,12 |
| 84 | 99,8490 | 107,00 |
| 93 | 99,7285 | 86,11 |
| 94 | 99,6611 | 29,72 |

La Bretagne (code 53) est la zone la plus divergente de cette comparaison à 100 m : elle illustre l'importance du traitement des îles, des traits de côte et des auto-intersections. **Ne pas assimiler ces 166,49 km² à une modification administrative effective.**

## Conséquences éditoriales pour Lieux

- **Continuité administrative documentée** des codes et appartenances départementales à la date des deux instantanés, sans créer d'autorités Pactols supplémentaires.
- **Ne pas dupliquer les limites 2026 comme géométrie historique officielle pour 2017–2025** sur la seule foi de cette continuité.
- Rechercher des **archives géographiques réellement millésimées**, distinctes de l'année de téléchargement ou de reconstruction ; figer empreintes, édition, code et géométrie.
- Les répertoires de données cartographiques historiques identifiés sont : **2018, 2019, 2021, 2022, 2023, 2024, 2025**. Les années **2017 et 2020** n'apparaissent pas dans l'index consulté ; ce constat ne prouve pas qu'aucune autre source existe.
- Le **COG annuel** de chaque millésime reste indispensable pour certifier les libellés, les rattachements et les états administratifs propres à cette année. Comparer un GeoJSON daté à la liste de codes COG **2026** est un **contrôle provisoire**, pas une validation temporelle.
- Jusqu'à validation, poursuivre dans Leaflet l'affichage de **repères datés et non historiques** (tracés pointillés) pour les années sans couche qualifiée.

Sources : https://www.data.gouv.fr/datasets/contours-administratifs ; https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/ ; https://www.insee.fr/fr/information/8740222 .

## Contrôle complémentaire du lot 2018

Les archives 2018 publiées à 100 m ont été acquises : `regions-2018.geojson.gz` (SHA-256 `24aab871b958675ed5aff9162229ea5abfcd55c1d15f13ee43a916b7558d37ca`) et `departements-2018.geojson.gz` (SHA-256 `cfbc29aa611707116bd364f070cc990591f929a8d25e8633ccef92f46f001667`).

- Les **18 régions et 101 départements** sont présents et sans code dupliqué, sans géométrie vide ou invalide lors du contrôle initial.
- Les **101 rattachements régionaux déclarés** dans les archives départementales 2018 sont identiques à ceux du COG 2026 de référence.
- Les 13 géométries régionales métropolitaines 2018 comparées à l'édition 2026 présentent des IoU compris entre **99,34668 % et 99,95665 %** ; elles ne sont pas identiques.
- L'audit des autres millésimes doit être terminé séparément ; ce premier lot ne vaut pas qualification collective des 14 archives attendues.

**2017 et 2020 :** absents du répertoire d'archives Etalab consulté, mais l'IGN décrit une offre **ADMIN EXPRESS historique depuis 2017**. Cette piste institutionnelle doit être instruite avant de conclure à l'indisponibilité définitive des contours (voir https://www.data.gouv.fr/pages/donnees-geographiques).

**Statut : note de recette, pas d'ajout de fichiers `docs/`.**
