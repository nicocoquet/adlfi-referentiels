# Guadeloupe — recette GEOFLA 2015 et contours Etalab 2026

**17 novembre 2026. Audit cartographique non validant, sans publication de polygones.**

## Objet et contexte

Après les PR 54 et 55, la Guadeloupe dispose de **32 alignements Pactols–COG validés pour 2026** et de **35 épisodes historiques documentaires**, dont deux anciens codes `97123` (Saint-Barthélemy) et `97127` (Saint-Martin), terminés en 2007.

La comparaison cartographique porte **exclusivement sur les 32 codes 971 encore courants en 2026**. Il serait erroné d'intégrer les deux anciens codes 97123 et 97127 à un total de 34 communes en 2015 ou 2026 ; ils sont conservés dans les fiches historiques mais exclus de cette comparaison de partitions contemporaines.

## Sources

- Archive candidate **GEOFLA 2015** : `GEOFLA_2-1_COMMUNE_SHP_UTM20W84GUAD_D971_2015-12-01.rar`, localisée dans le [miroir documentaire GitHub justinelliotmeyers](https://github.com/justinelliotmeyers/official_france_administrative_boundary_shapefile). L'empreinte de la copie acquise et contrôlée est désormais figée (voir ci-dessous). **La présence dans ce dépôt tiers et la nomenclature ne suffisent pas à authentifier le fichier comme un original IGN.**
- [Contours administratifs Etalab 2026, data.gouv.fr](https://www.data.gouv.fr/datasets/contours-administratifs), généralisations 100 m et 50 m, issues des sources administratives nationales. Empreintes SHA-256 déjà figées dans le dépôt : respectivement `4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778` et `6db43cd98a7211516da64e91761100504ba3feeddc986ebe0d50f84df624cd38`.
- Documentation produit [GEOFLA, IGN](https://geoservices.ign.fr/sites/default/files/2021-07/DC_GEOFLA_2-2.pdf) : produit cartographique généralisé destiné à des usages proches du 1:1 000 000, dernière édition documentée en 2016 ; ses limites et dates ne sont pas assimilables automatiquement à une délimitation juridique exacte.

## Méthode

1. Inventorier les fichiers SHP/PRJ du RAR et vérifier la projection **déclarée dans le WKT source**, sans la déduire uniquement du nom UTM20W84GUAD.
2. Lire les **codes INSEE attributaires des 32 communes** ; refuser les doublons, les codes hors département ainsi que les anciens 97123 et 97127 si ceux-ci étaient mêlés à la couche de 2015.
3. Vérifier la validité des géométries et l'absence de recouvrement surfacique, projeter les trois partitions dans **EPSG:6933** pour les mesures.
4. Comparer GEOFLA 2015 avec Etalab 2026 à 100 m, puis 50 m ; mesurer aussi la sensibilité au niveau de généralisation entre les deux dessins 2026.
5. Décomposer le cumul des écarts des 32 communes en : **différence d'emprise extérieure + deux fois la différence de répartition interne entre codes** ; vérifier la fermeture de l'équation avant archivage.
6. Localiser les principales divergences de contour par leur **aire, point intérieur représentatif et rectangle approximatif** en WGS84, sans exporter de polygone.
7. Générer deux fois le rapport avec les mêmes sources et comparer les octets ; archiver uniquement les métriques et la provenance dans un artefact de CI.

La CI spécialisée contrôle séparément les sources, les codes, la topologie et les métriques. Les résultats obtenus figurent ci-dessous ; la copie candidate 2015 est épinglée par son SHA-256.

## Résultats mesurés dans la recette

[CI géométrique n°44018152128 réussie](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44018152128), [artefact JSON de recette](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44018152128/artifacts/14298894872).

### Identification et reproductibilité

- Archive candidate GEOFLA 2015 : `GEOFLA_2-1_COMMUNE_SHP_UTM20W84GUAD_D971_2015-12-01.rar`, **SHA-256 `e33e412d840e27e01df70c811241481199e2bf4fa9597a8c19a5f7255b5693df`**, désormais figé dans le script et la CI.
- Livraison : `1_DONNEES_LIVRAISON_2015/GEOFLA_2-1_SHP_UTM20W84GUAD_D971-ED152/COMMUNE/`, avec couches `COMMUNE` et `LIMITE_COMMUNE`.
- **32 objets polygonaux, 32 codes attributaires INSEE_COM**, aucun code 97123 ou 97127 dans le jeu des communes actuelles.
- Projection WKT source : **WGS 84 / UTM 20N, EPSG:32620**, PRJ SHA-256 `251e5e5bcccb92f6358564951f89c7e2464b0cf63200a9fc55d2d11c23157424`. La correspondance du WKT à EPSG:32620 est vérifiée indépendamment du nom de l'archive.
- Rapport produit deux fois avec des résultats identiques octet pour octet. **Aucun polygone archivé ni diffusé**.

### Décomposition surfacique en EPSG:6933

| Grandeur | Comparaison 2015 / 2026 à 100 m | Comparaison 2015 / 2026 à 50 m |
| --- | ---: | ---: |
| Aire d'emprise GEOFLA 2015 | 1 631,828990 km² | 1 631,828990 km² |
| Aire d'emprise Etalab 2026 | 1 632,484050 km² | 1 633,373185 km² |
| **Différence symétrique d'emprise extérieure** | **20,473639 km²** | **20,897009 km²** |
| Dessin 2015 hors de l'emprise 2026 | 9,909289 km² | 9,676407 km² |
| Dessin 2026 hors de l'emprise 2015 | 10,564349 km² | 11,220602 km² |
| **Écart interne unique entre codes communaux** | **16,897550 km²** | **16,761591 km²** |
| Cumul des différences des 32 communes | **54,268739 km²** | **54,420191 km²** |

Les égalités vérifiées sur les géométries non arrondies sont : **cumul des différences communales = différence extérieure + 2 × différence intérieure unique**. Les très faibles différences au dernier chiffre décimal peuvent provenir des arrondis du tableau.

**Test de généralisation 2026 :** les emprises 2026 à **100 m et 50 m** diffèrent de **8,079128 km²** en différence symétrique. Utiliser la référence 50 m à la place de 100 m modifie l'écart global mesuré avec 2015 de **0,423370 km²**, ce qui ne suffit pas à expliquer les autres divergences. Les effets de généralisation locale restent néanmoins importants.

### Six communes prioritaires pour l'examen géographique

| Code | Commune | Écart total à 100 m | Part d'emprise extérieure dans l'écart |
| --- | --- | ---: | ---: |
| 97117 | Le Moule | **3,333675 km²** | 41,887 % |
| 97129 | Sainte-Rose | **3,168546 km²** | 37,592 % |
| 97119 | Petit-Canal | **2,980410 km²** | 27,530 % |
| 97115 | Lamentin | **2,860348 km²** | 11,605 % |
| 97116 | Morne-à-l’Eau | **2,685930 km²** | 17,763 % |
| 97118 | Petit-Bourg | **2,334115 km²** | 23,324 % |

Ces chiffres montrent que les différences de maillage interne occupent une place substantielle dans plusieurs communes. Ils ne démontrent **aucun déplacement juridique** d'une limite.

### Localisations descriptives des principales composantes extérieures

Les points ci-dessous se trouvent **à l'intérieur des composantes de différence des deux dessins**, sans représenter des bornes, centres communaux ou événements territoriaux.

| Sens de la comparaison | Surface d'une composante significative | Longitude du point intérieur | Latitude |
| --- | ---: | ---: | ---: |
| Dessin GEOFLA 2015 hors emprise Etalab 2026 100 m | 0,329662 km² | –61,797563 | 16,307300 |
| Dessin GEOFLA 2015 hors emprise Etalab 2026 100 m | 0,267740 km² | –61,398419 | 16,429500 |
| Dessin Etalab 2026 100 m hors emprise GEOFLA 2015 | 0,795735 km² | –61,591004 | 15,837150 |
| Dessin Etalab 2026 100 m hors emprise GEOFLA 2015 | 0,365439 km² | –61,594105 | 15,873500 |

Les composantes sont beaucoup moins concentrées que celles détectées en Martinique et en Guyane. L'absence d'un bloc dominant n'autorise pas pour autant une conclusion sur la nature de chaque limite : elle exige le rapprochement avec des sources côtières ou hydrographiques documentées.

### Limite documentaire

L'intégrité du RAR candidat est désormais contrôlée par SHA-256 ; son **authenticité vis-à-vis d'un original IGN** et la date d'effet des limites représentées restent à établir. Cette donnée de 2015 ne représente **ni le millésime 1946 ni les anciens codes 97123 et 97127 terminés en 2007**. Elle ne peut être publiée comme cartographie historique sans qualification complémentaire.

## Interprétation strictement limitée

Une différence mesurée entre GEOFLA 2015 et Etalab 2026 peut résulter du **trait de côte représenté, de la généralisation, d'autres méthodes de production ou de véritables transformations** ; l'audit n'est pas en mesure d'en identifier la cause juridique.

**Aucun contour 2015 ou 2026 n'est publié comme limite historique, aucune ancienne commune 971 n'est réintroduite dans le millésime 2026, aucun ARK Pactols ni relation de succession ne sont modifiés.**

Fichiers : `scripts/auditer_geofla_guadeloupe_2015.py`, `tests/test_auditer_geofla_guadeloupe_2015.py`, `.github/workflows/lieux-guadeloupe-geofla-2015.yml`.
