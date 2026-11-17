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

### Source candidate et contrôles de reproductibilité

La [CI spatiale n°44021856933](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44021856933) est **réussie**, ainsi que la [CI générale n°44021857030](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44021857030). [Rapport JSON numérique de recette](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44021856933/artifacts/14301387552).

- Archive candidate : **13 entrées**, **28 936 octets**, SHA-256 **`6ab4183681f0d15472678f958ca7a6a2c4b95b1b3bc694f7aefe7ec4c67dfea2`**, contrôlé au téléchargement.
- Couche `COMMUNE.shp` : **24 objets**, 24 codes dans le champ attributaire `INSEE_COM`, distincts et concordants avec les codes `97401`–`97424`.
- Une couche `LIMITE_COMMUNE.shp` est également présente ; **elle n'est pas adoptée comme preuve historique**.
- Projection du fichier PRJ effectivement vérifiée : **RGR92 / UTM 40S, EPSG:2975**, WKT SHA-256 `9f2c2a2bcdc7af7b0f59407979ad01e295a2ab78afd1ca4bddfce145f838d355`.
- Toutes les géométries considérées sont valides et sans recouvrement surfacique de partition supérieur à la tolérance de calcul. **Deux rapports JSON ont été comparés octet à octet** et sont identiques.

### Décomposition mesurée des surfaces en EPSG:6933

| Grandeur (en km²) | GEOFLA 2015 / Etalab 2026 100 m | GEOFLA 2015 / Etalab 2026 50 m |
| --- | ---: | ---: |
| Emprise des 24 communes en 2015 | 2 502,161250 | 2 502,161250 |
| Emprise des 24 communes en 2026 | 2 503,416919 | 2 503,598017 |
| **Différence symétrique d'emprise extérieure** | **7,196579** | **7,273004** |
| Portion 2015 extérieure au dessin 2026 | 2,970455 | — |
| Portion 2026 extérieure au dessin 2015 | 4,226124 | — |
| **Différence de répartition intérieure unique entre codes** | **20,630913** | **20,640775** |
| **Cumul des différences par commune** | **48,458405** | **48,554554** |

Les chiffres satisfont l'équation `cumul des différences communales = différence extérieure + 2 × différence interne unique`, avec tolérance pour les arrondis décimaux des rapports.

La **différence symétrique d'emprise** entre les deux généralisations 2026 (50 m et 100 m) est **2,527438 km²** : c'est une sensibilité à la méthode de représentation pour une même édition, **pas une évolution territoriale**.

### Huit écarts communaux prioritaires, comparaison à 100 m

| Code | Commune | Différence symétrique (km²) | Fraction extérieure de l'écart |
| --- | --- | ---: | ---: |
| 97410 | Saint-Benoît | 3,920987 | 14,468 % |
| 97422 | Le Tampon | 3,564044 | 0 % |
| 97408 | La Possession | 3,089160 | 15,689 % |
| 97415 | Saint-Paul | 2,875816 | 19,781 % |
| 97421 | Salazie | 2,594722 | 0 % |
| 97403 | Entre-Deux | 2,496233 | 0 % |
| 97412 | Saint-Joseph | 2,443816 | 25,615 % |
| 97416 | Saint-Pierre | 2,349534 | 24,182 % |

Une part notable de la discordance concerne **les lignes de séparation entre les codes**, plutôt que la seule emprise côtière. Dans le cas du Tampon, l'écart mesuré relève entièrement de la redistribution interne des dessins.

### Examen ciblé Saint-Louis et Cilaos

- **Saint-Louis (97414)** : différence symétrique totale **1,795780 km²** (dont **1,762410 km²** de dessin intérieur rattaché à un code différent), Jaccard **98,201940 %**.
- **Cilaos (97424)** : différence symétrique totale **1,530492 km²**, **entièrement intérieure** à l'emprise commune des deux éditions, Jaccard **98,203430 %**.

Ces métriques concernent les géométries **2015 et 2026**, lorsque la division du **5 février 1965** est déjà intervenue. **Elles ne mesurent donc pas la surface distraite de Saint-Louis lors de la création de Cilaos.** Une restitution de la limite antérieure à 1965 exige une source géographique plus ancienne et qualifiée.

### Composantes extérieures principales (100 m)

Les deux sens du différentiel extérieur comprennent chacun **156 composantes**. Exemples d'emplacements *intérieurs aux zones où les dessins diffèrent* (WGS84) :

| Sens | Aire composante (km²) | Longitude | Latitude |
| --- | ---: | ---: | ---: |
| GEOFLA 2015 hors 2026 | 0,168446 | 55,270536 | –21,133357 |
| GEOFLA 2015 hors 2026 | 0,134020 | 55,579678 | –20,895871 |
| Etalab 2026 hors 2015 | 0,357559 | 55,702138 | –21,015279 |
| Etalab 2026 hors 2015 | 0,355077 | 55,450152 | –20,874450 |

Ces points ne sont ni des limites, ni des bornes de commune ; aucun polygone n'a été exporté.

### Interprétation et réserve

Le SHA-256 garantit la stabilité de la **copie effectivement téléchargée**, pas son authenticité comme source originale IGN. Les écarts peuvent dépendre de la méthode de généralisation, des tracés côtiers, des choix de représentation ou d'autres révisions cartographiques. **Aucun mouvement administratif nouveau n'est déduit de ces mesures.**

**Aucun fichier dans `docs/` n'est modifié. Aucun alignement Pactols, contour historique ou lien de succession n'est créé.**
