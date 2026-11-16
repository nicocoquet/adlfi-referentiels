# Régions et départements : qualification des millésimes 2018–2025

**16 novembre 2026 — recette scientifique, sans publication sur Pages · PR #36.**

## Corpus et sources

- Contours généralisés à **100 m**, issus des archives géographiques Etalab / IGN : sept années réellement disponibles (**2018, 2019, 2021, 2022, 2023, 2024 et 2025**) et deux couches par année (**régions, départements**), soit **14 archives**.
- Code officiel géographique de l'Insee **au 1er janvier de chaque année**, acquis dans ses fichiers d'origine : archives texte 2018 et ensembles CSV 2019, 2021–2025. Huit ZIP Insee, avec empreintes SHA-256 figées dans le script `qualifier_cog_annuels_regions_departements.py`.
- Les empreintes SHA-256 des 14 archives cartographiques sont figées dans `auditer_contours_region_departement_2018_2025.py`.
- Les **2017 et 2020** ne sont pas présents dans l'archive Etalab examinée. L'existence possible de géométries issues des éditions historiques **ADMIN EXPRESS IGN** reste à instruire : l'absence dans cet hébergement ne signifie pas absence dans toute autre source.

Source Insee : https://www.insee.fr/fr/information/2560452 .
Source des archives géographiques : https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/ .

## Résultats des contrôles annuels

Pour **chacune des sept années** : 18 régions et 101 départements, présents à la fois dans l'archive cartographique et dans le COG Insee correspondant.

- **Aucun code absent ou supplémentaire** aux deux échelons (après exclusion explicite des huit territoires de statut différent rencontrés dans certaines éditions).
- **Aucun rattachement département–région divergent** entre les couches SIG et le COG annuel.
- **Aucun libellé différent** entre les listes officielles et les archives cartographiques, après normalisation des accents, espaces et ponctuations.
- Le contrôle **2019** tient compte du schéma Insee en minuscules, distinct des autres millésimes.
- La comparaison avec 2026 n'est conservée qu'à titre métrique ; elle **n'a pas valeur de datation rétroactive** pour les frontières.

## Topologie : anomalies cartographiques à corriger avant intégration

| Millésime | Échelon | Codes des géométries non valides | Origine du défaut |
|---|---|---|---|
| 2018 | Région / département | Aucune | — |
| 2019 | Région | **53** (Bretagne) | Auto-intersection |
| 2019 | Département | **22** (Côtes-d'Armor), **39** (Jura), **71** (Saône-et-Loire) | Auto-intersections |
| 2021 | Région / département | Aucune | — |
| 2022 | Région / département | Aucune dans les 18 / 101 codes COG | Les géométries des COM, exclues du lot, ont leurs propres anomalies |
| 2023 | Région / département | Aucune dans les 18 / 101 codes COG | Même distinction |
| 2024 | Région / département | Aucune dans les 18 / 101 codes COG | Même distinction |
| 2025 | Région | **53** (Bretagne) | Auto-intersection |
| 2025 | Département | **22** (Côtes-d'Armor) | Auto-intersection |

**Six occurrences de géométries invalides au total.** Les réparations seront réalisées sur une copie de travail, avec conservation des originaux et contrôle du changement d'aire en Lambert-93. Pour les départements **39 et 71** de 2019, `make_valid` produit une `GeometryCollection` contenant des éléments non surfaciques : seule sa partie surfacique pourra être retenue, après mesure et qualification. La chaîne doit bloquer toute autre anomalie ou réparation excessive.

## Décision de structuration

Chaque couche intégrée devra porter séparément :

1. `annee_COG` et `date_reference_COG` : 1er janvier de l'année, identité administrative attestée par Insee ;
2. `annee_geometrie` et `source_geometrie` : édition Etalab/IGN utilisée ;
3. `source_SHA256` et `source_COG_SHA256` : audit reproductible ;
4. `corrections_geometriques` : éventuelles réparations mesurées et documentées.

Ne pas écrire que les polygones sont identiques entre 2016 et 2026 : les archives montrent des écarts, notamment côtiers, même sans changement de région. Les différences ne prouvent **pas** à elles seules un transfert territorial.

**Aucun nouveau lien Pactols–COG. Aucun changement du site public au stade de ce rapport.**
