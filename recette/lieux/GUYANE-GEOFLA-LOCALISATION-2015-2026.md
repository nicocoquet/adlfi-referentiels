# Guyane — localisation des divergences GEOFLA 2015 / Etalab 2026

**16 novembre 2026. Recette non publiée : contours historiques non validés.**

## Objectif

L'audit précédent a établi une différence symétrique des emprises 2015–2026 de **733,434981 km²**. Pour Régina (97301), Sinnamary (97312) et Iracoubo (97303), plus de 93 % des écarts individuels se situent hors de l'emprise commune des deux dessins.

L'objectif est de **localiser les principales composantes de ces différences**, sans leur attribuer une cause juridique, hydrographique ou côtière. Un second contrôle comparera les généralisations **50 m et 100 m du même millésime 2026**, afin de documenter la sensibilité du résultat au niveau de détail cartographique.

## Sources

- GEOFLA Guyane 2015 : **GEOFLA_2-1_COMMUNE_SHP_UTM22RGFG95_D973_2015-12-01.rar**, copie externe non authentifiée directement par une archive IGN. SHA-256 **3aac9e8b979118b25df48e9ef21fc1029d735cc3c99a025cd1f5688560f41298**.
- [Contours administratifs data.gouv.fr](https://www.data.gouv.fr/datasets/contours-administratifs), millésime 2026, édition du **4 mai 2026**, produits généralisés à **100 m et 50 m**, principalement issus d'ADMIN EXPRESS de l'IGN pour les DROM.
- Contours 2026 à 100 m : SHA-256 **4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778**.
- Contours 2026 à 50 m : SHA-256 **6db43cd98a7211516da64e91761100504ba3feeddc986ebe0d50f84df624cd38** (première CI réussie, désormais épinglée).

**Les différentes généralisations de 2026 ne représentent pas des dates administratives différentes.** Elles permettent seulement une comparaison interne à une famille de produits du même millésime.

## Méthode

1. Vérifier l'intégrité et les codes INSEE des **22 communes de Guyane**, puis lire le WKT de la copie 2015.
2. Reprojeter les trois jeux de données en **EPSG:6933** et calculer leurs différences de surface et leurs indices de recouvrement.
3. Décomposer la différence d'emprise extérieure en composantes ; relever **l'aire**, un **point intérieur représentatif** et une **enveloppe rectangulaire approximative** (WGS84) pour les composants les plus significatifs de Régina, Sinnamary et Iracoubo.
4. Comparer les résultats 2015/2026 à 100 m et à 50 m, ainsi que **2026 à 100 m/2026 à 50 m**.
5. Contrôler les équations et la reproductibilité par tests, puis archiver **uniquement le rapport de métriques** dans GitHub Actions.

Les points et enveloppes sont des pistes de diagnostic : ils ne sont ni des bornes ni des contours administratifs, et ils ne permettent pas de déduire qu'une limite aurait effectivement changé entre les deux dates.

## Résultats réels — CI n°43948883458

[Exécution GitHub Actions : sources contrôlées et deux calculs reproductibles](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43948883458). [Artefact JSON de recette](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43948883458/artifacts/14265882600).

### Comparaisons de l'emprise complète de Guyane

| Comparaison | Différence symétrique | Aire 2015 non représentée dans la seconde édition |
| --- | ---: | ---: |
| GEOFLA 2015 / Etalab 2026 100 m | 733,434981 km² | 678,554599 km² |
| GEOFLA 2015 / Etalab 2026 50 m | 733,142348 km² | 678,493686 km² |
| Etalab 2026 100 m / Etalab 2026 50 m | **21,968320 km²** | 11,069563 km² (100 m hors 50 m) |

La comparaison de GEOFLA 2015 avec 2026 à 50 m modifie l'écart global de **0,292633 km²** seulement par rapport à la référence à 100 m. Le changement de niveau de généralisation **50 m / 100 m** n'explique pas l'ordre de grandeur des différences avec 2015. Il ne permet cependant pas de quantifier l'effet des différences entre GEOFLA 2015 et les méthodes d'ADMIN EXPRESS 2026, ni d'authentifier les limites juridiques.

### Communes prioritaires, sensibilité à l'échelle

| Code et commune | Écart total avec 2026 100 m | Écart total avec 2026 50 m | Écart 50 m / 100 m du seul millésime 2026 |
| --- | ---: | ---: | ---: |
| 97301 Régina | 267,618413 km² | 266,479839 km² | 6,804266 km² |
| 97312 Sinnamary | 159,664326 km² | 160,005084 km² | 4,177757 km² |
| 97303 Iracoubo | 133,782800 km² | 133,768158 km² | 3,972672 km² |

### Localisation des plus grandes composantes de l'écart extérieur

Les résultats ci-dessous concernent exclusivement les zones **présentes sur le dessin GEOFLA 2015 mais absentes de l'emprise totale représentée en 2026 à 100 m**.

| Commune | Aire d'une composante dominante | Longitude du point intérieur | Latitude du point intérieur | Enveloppe approximative, WGS84 (longitude min / max ; latitude min / max) |
| --- | ---: | ---: | ---: | --- |
| Régina | **244,663506 km²** | –51,962305 | 4,610350 | –52,168000 / –51,923100 ; 4,406600 / 4,812140 |
| Sinnamary | **151,222327 km²** | –52,938101 | 5,415110 | –53,169942 / –52,806935 ; 5,307362 / 5,521855 |
| Iracoubo | **123,708050 km²** | –53,199509 | 5,500680 | –53,469387 / –53,089752 ; 5,433200 / 5,568883 |

Ces **trois composantes réunies représentent environ 519,594 km²**, soit **76,6 %** de l'aire totale que le dessin de 2015 représente en dehors de l'emprise 2026 à 100 m, tous codes communaux confondus.

Le test à **50 m confirme la stabilité générale des mêmes grandes composantes** : respectivement **244,783314 km²**, **151,497013 km²** et **123,806557 km²**. Une localisation indépendante et une analyse documentaire des tracés restent nécessaires pour établir s'il s'agit de représentation du littoral, d'hydrographie, de frontière internationale, d'îles, d'écarts de généralisation ou de différences de source.

**Aucun de ces points ne représente une frontière juridique, un acte historique ou le centre d'une commune.** Il s'agit de points intérieurs à des polygones de différence calculés, et non de nouvelles autorités géographiques.

## Vérifications indispensables avant qualification

La localisation comme **littoral**, **cours d'eau frontalier** ou **limite interne** exige une source hydrographique ou côtière indépendante et datée. Le document de [nomenclature IGN](https://data.geopf.fr/annexes/ressources/documentation/Nomenclature_paquets.pdf) confirme le modèle de dénomination d'un paquet GEOFLA, **pas l'intégrité de la copie de 2015**. L'[API de téléchargement de l'IGN](https://www.data.gouv.fr/dataservices/api-geoplateforme-telechargement) est à explorer pour la recherche d'un exemplaire original ou d'un paquet officiellement conservé.

**Cet audit ne publie aucun polygone, ne valide aucune géométrie ancienne et ne modifie ni les 22 liens Pactols–COG approuvés pour 2026 ni les fiches historiques du référentiel Lieux.**

## Fichiers

Script : scripts/localiser_ecarts_geofla_guyane.py.

Tests : tests/test_localiser_ecarts_geofla_guyane.py.

CI : .github/workflows/lieux-guyane-localisation-ecarts.yml.

Rapport : artefact temporaire GitHub Actions, contenant des mesures, points représentatifs et enveloppes sans frontières publiables.
