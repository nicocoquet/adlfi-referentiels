# La Réunion — comparaison cartographique GEOFLA 2015 et Etalab 2026

**17 novembre 2026. Recette spatiale non validante, sans publication de polygones.**

## Finalité

Après les [PR 57](https://github.com/nicocoquet/adlfi-referentiels/pull/57), [58](https://github.com/nicocoquet/adlfi-referentiels/pull/58) et [59](https://github.com/nicocoquet/adlfi-referentiels/pull/59), les **24 communes de La Réunion** possèdent un alignement Pactols–COG approuvé **pour 2026** ainsi qu'une chronologie documentaire COG (**24 épisodes, 25 lignes de mouvements**).

La division de **Saint-Louis (97414) en Saint-Louis (97414) et Cilaos (97424)**, le **5 février 1965**, est établie par le COG, mais **aucune source géométrique ne permet à ce stade de tracer directement la limite de 1965**. Comparer un dessin de 2015 à un dessin de 2026 ne suffit pas à reconstruire les limites de 1964 ou 1965.

## Sources et garanties de provenance

- Archive candidate **GEOFLA 2015, commune D974** : `GEOFLA_2-1_COMMUNE_SHP_RGR92UTM40S_D974_2015-12-01.rar`, repérée dans le [miroir tiers justinelliotmeyers](https://github.com/justinelliotmeyers/official_france_administrative_boundary_shapefile). **Ce miroir ne prouve pas l'authenticité du paquet IGN original.**
- La première étape GitHub Actions inventorie l'archive, publie son empreinte **SHA-256 réellement mesurée**, son schéma et le WKT de projection. Le nom suggère RGR92 / UTM 40S, mais le code EPSG et la cohérence des coordonnées doivent être confirmés sur le PRJ.
- [Etalab — Contours administratifs](https://www.data.gouv.fr/datasets/contours-administratifs) : édition 2026-05-04 aux généralisations **100 m** et **50 m**. SHA-256 des deux jeux déjà épinglés dans le dépôt : `4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778` et `6db43cd98a7211516da64e91761100504ba3feeddc986ebe0d50f84df624cd38`.
- [Documentation IGN GEOFLA](https://geoservices.ign.fr/sites/default/files/2021-07/DC_GEOFLA_2-2.pdf) : données généralisées, non assimilables à la connaissance juridique exacte des limites.

## Protocole à mettre en œuvre après qualification de la copie

1. Contrôler archive, SHA-256, fichiers SHP/PRJ, CRS et **24 codes communaux distincts** en 2015 ; vérifier la cohérence avec les 24 codes du COG au 1er janvier 2026.
2. Contrôler la validité topologique des 24 géométries de chaque édition et l'absence de recouvrement surfacique à l'intérieur d'une partition.
3. Transformer les trois partitions dans une projection équivalente surfacique (EPSG:6933) ; comparer **2015 / 2026 (100 m)** et **2015 / 2026 (50 m)**.
4. Mesurer la différence d'emprise extérieure et la différence interne unique entre codes, avec test de fermeture : `cumul des différences communales = différence extérieure + 2 × différence interne`.
5. Mesurer la différence entre **2026 50 m** et **2026 100 m** pour caractériser la sensibilité à la généralisation.
6. Identifier les communes présentant le plus grand écart, notamment vérifier séparément Saint-Louis et Cilaos ; ce classement **n'est pas une preuve d'évolution juridique**.
7. Ne publier que des métriques numériques et des localisations ponctuelles descriptives, jamais des polygones issus du dossier candidat.

## Résultats

**Inventaire source engagé.** Les métriques seront consignées ici uniquement lorsqu'elles auront été réellement exécutées et vérifiées par GitHub Actions.

**Aucun fichier dans `docs/` n'est modifié. Aucun alignement Pactols, contour historique ou lien de succession n'est créé.**
