# Martinique — contrôle cartographique GEOFLA 2015 / Etalab 2026

**17 novembre 2026 · Audit en recette, indépendant de la publication des 34 alignements Pactols et des états COG historiques.**

## Enjeu

La Martinique dispose désormais dans Lieux de **34 correspondances Pactols–COG approuvées pour le 1er janvier 2026**, et de **34 épisodes documentaires historiques COG**. Les géométries 2026 des 34 communes sont présentes et topologiquement valides mais ne constituent pas des contours historiques pour les années 1943–2025.

Avant tout ajout de contours anciens au navigateur, il faut mesurer la divergence entre une édition cartographique GEOFLA et l'édition nationale 2026, et séparer les **écarts d'emprise extérieure** des **écarts de répartition du maillage intercommunal**.

## Sources et provenance

1. Paquet candidat GEOFLA 2015 : `GEOFLA_2-1_COMMUNE_SHP_UTM20W84MART_D972_2015-12-01.rar`, présent sur le [miroir documentaire GitHub justinelliotmeyers](https://github.com/justinelliotmeyers/official_france_administrative_boundary_shapefile). Il est **présumé correspondre à une édition IGN**, mais il n'est **pas encore authentifié par comparaison avec un original IGN**. Le nom du paquet ne démontre ni l'intégrité des fichiers, ni la date d'effet des limites.
2. [Contours administratifs nationaux 2026 (data.gouv.fr)](https://www.data.gouv.fr/datasets/contours-administratifs) : éditions à **100 m** et **50 m** datées du 4 mai 2026, avec empreintes SHA-256 déjà contrôlées, respectivement `4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778` et `6db43cd98a7211516da64e91761100504ba3feeddc986ebe0d50f84df624cd38`.
3. [Historique des données géographiques, data.gouv.fr](https://www.data.gouv.fr/pages/donnees-geographiques) : documentation de la disponibilité de GEOFLA sur les périodes anciennes et du remplacement de la chaîne par ADMIN EXPRESS.

**Attention :** une diffusion `GEOFLA - centres bourgs` ne constitue **pas** une couche polygonale des limites de communes. Elle n'est pas retenue pour cette comparaison.

## Méthode

- Inventorier les fichiers SHP/PRJ contenus dans l'archive RAR après contrôle des chemins, déduire le **CRS du WKT réellement fourni**, contrôler le domaine géographique de Martinique et lire les **codes INSEE attributaires**, sans inférer d'identité par nom ou localisation.
- Confirmer exactement **34 codes 97201–97234** identifiés sans doublon, avec polygones valides. Projeter les trois séries dans **EPSG:6933** pour le calcul des surfaces.
- Comparer **GEOFLA 2015 / Etalab 2026 à 100 m**, **GEOFLA 2015 / Etalab 2026 à 50 m** et la **sensibilité à la généralisation 50 m / 100 m de la seule édition 2026**.
- Séparer la différence symétrique de l'**emprise totale** et les changements de code dans l'emprise commune. Sur des partitions communales sans recouvrements : somme des différences par commune = différence d'emprise externe + deux fois les différences internes.
- Documenter les **principales communes divergentes** et les grandes composantes de différence de l'emprise externe au moyen de leur **surface, d'un point intérieur et d'une enveloppe approximative**. Aucun polygone ancien ou nouveau n'est exporté.
- Produire deux fois le rapport JSON et en contrôler l'identité octet à octet. Les premiers résultats doivent permettre de **figer le SHA-256 de la copie 2015**, puis de relancer l'analyse avec cette garantie d'intégrité documentaire.

## Portée de l'étude

Le calcul concerne des **différences entre représentations cartographiques**, susceptibles de refléter des changements de méthode, de généralisation, de description du littoral ou d'autres facteurs. Il **ne démontre aucun changement juridique** entre 2015 et 2026. La preuve d'une évolution de limite administrative nécessiterait une référence historique datée et une source réglementaire, distinctes de ces mesures.

La branche n'altère pas `docs/`. Les **34 correspondances Pactols–COG** et les **34 fiches documentaires historiques** déjà publiées demeurent inchangées.

## Livrables

- `scripts/auditer_geofla_martinique_2015.py` : lecture et mesures sans polygone exporté.
- `tests/test_auditer_geofla_martinique_2015.py` : fermeture des partitions et des écarts.
- `.github/workflows/lieux-martinique-geofla-2015.yml` : acquisition des sources, contrôles de projection et de SHA, double exécution et artefact JSON de recette.

## Résultats de la recette — copie 2015 inspectée

[CI spécialisée initiale réussie n°44013086518](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44013086518). [Rapport JSON de recette](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44013086518/artifacts/14297586332).

L'archive a été lue et testée deux fois, avec **rapport identique octet pour octet** :

- **Empreinte SHA-256 du RAR candidat 2015 :** `877c32184e42c012f563ab50240b64cd70a41b507a31d042ff8c6823d3ef787a`, désormais épinglée dans le script et la CI.
- Sous-répertoire source : `1_DONNEES_LIVRAISON_2015/GEOFLA_2-1_SHP_UTM20W84MART_D972-ED152/COMMUNE/`.
- **Deux couches SHP** : `COMMUNE` et `LIMITE_COMMUNE` ; contrôle des géométries effectué sur `COMMUNE`.
- Code INSEE attesté par le champ **`INSEE_COM` pour 34/34 objets** ; aucun doublon et aucun code hors Martinique.
- WKT du fichier `.prj` : **WGS 84 / UTM 20N, équivalent EPSG:32620**, avec projection centrale à –63°, faux-est à 500 000 m, facteur d'échelle 0,9996. Empreinte du PRJ : `251e5e5bcccb92f6358564951f89c7e2464b0cf63200a9fc55d2d11c23157424`.
- Contours Etalab 2026 : exactement **34 codes correspondants** à 100 m et à 50 m. Les 3 partitions sont exploitables sans recouvrement surfacique au-delà des tolérances techniques.

### Écarts d'emprise et de maillage

| Grandeur, calculée en EPSG:6933 | GEOFLA 2015 / Etalab 2026 à 100 m | GEOFLA 2015 / Etalab 2026 à 50 m |
| --- | ---: | ---: |
| Surface de l'emprise commune de l'édition GEOFLA 2015 | 1 103,290338 km² | 1 103,290338 km² |
| Surface totale de l'édition 2026 | 1 085,123753 km² | 1 085,964332 km² |
| **Différence symétrique des contours extérieurs** | **31,630156 km²** | **31,528409 km²** |
| Présent dans le dessin 2015, absent de l'emprise 2026 | 24,898371 km² | 24,427208 km² |
| Présent dans le dessin 2026, absent de l'emprise 2015 | 6,731785 km² | 7,101201 km² |
| **Écart interne unique entre codes communaux** | **18,497758 km²** | **18,867088 km²** |
| Cumul des 34 différences par code | 68,625671 km² | 69,262586 km² |

L'identité est contrôlée sur les géométries non arrondies : **cumul des écarts communaux = différence extérieure + 2 × écart intérieur unique**. Les résidus éventuels de 0,000001 km² proviennent de l'arrondi final des mesures.

**Sensibilité à la généralisation 2026 :** les deux emprises 2026 à 50 m et 100 m diffèrent entre elles de **9,411333 km²**. Pourtant, remplacer 2026 à 100 m par 2026 à 50 m ne modifie la différence symétrique avec GEOFLA 2015 que de **0,101747 km²**. La variation de cette **mesure globale** est petite ; elle n'implique pas que les détails locaux soient identiques, puisque les deux généralisations 2026 présentent elles-mêmes des écarts.

### Communes présentant les plus grandes différences

| Code | Commune | Différence symétrique totale à 100 m | Part liée à l'emprise extérieure |
| --- | --- | ---: | ---: |
| 97213 | Le Lamentin | **7,436386 km²** | 78,272 % |
| 97221 | Rivière-Salée | **4,365785 km²** | 74,783 % |
| 97207 | Ducos | **3,817755 km²** | 69,282 % |
| 97222 | Le Robert | **3,698159 km²** | 67,855 % |
| 97232 | Le Vauclin | **3,106914 km²** | 68,141 % |
| 97210 | Le François | **3,079283 km²** | 53,495 % |

Ces communes doivent être **contrôlées géographiquement** avant qu'une explication littorale, hydrographique ou administrative soit retenue.

### Limites de preuve

L'identification du modèle GEOFLA et la correspondance du WKT, de la structure de livraison et des 34 codes **renforcent la cohérence documentaire de la copie**, mais **n'authentifient pas** son empreinte auprès de l'IGN. Le descriptif officiel [GEOFLA version 2.2](https://geoservices.ign.fr/sites/default/files/2021-07/DC_GEOFLA_2-2.pdf) indique que le produit est une carte généralisée pour des usages proches du **1:1 000 000**, que ses informations peuvent avoir **jusqu'à un an d'ancienneté à la date d'édition** et que sa dernière édition est **2016**. Il serait donc erroné d'assimiler automatiquement les contours de l'archive estampillée 2015 à une situation administrative exacte au 1er janvier 2015.

**Aucune représentation géométrique 2015 ou 2026 n'est promue dans Lieux à titre de contour historique.** L'analyse reste une recette spatialement quantifiée, pas une validation des limites territoriales.


