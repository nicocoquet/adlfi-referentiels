# Guyane — localisation des divergences GEOFLA 2015 / Etalab 2026

**16 novembre 2026. Recette non publiée : contours historiques non validés.**

## Objectif

L'audit précédent a établi une différence symétrique des emprises 2015–2026 de **733,434981 km²**. Pour Régina (97301), Sinnamary (97312) et Iracoubo (97303), plus de 93 % des écarts individuels se situent hors de l'emprise commune des deux dessins.

L'objectif est de **localiser les principales composantes de ces différences**, sans leur attribuer une cause juridique, hydrographique ou côtière. Un second contrôle comparera les généralisations **50 m et 100 m du même millésime 2026**, afin de documenter la sensibilité du résultat au niveau de détail cartographique.

## Sources

- GEOFLA Guyane 2015 : **GEOFLA_2-1_COMMUNE_SHP_UTM22RGFG95_D973_2015-12-01.rar**, copie externe non authentifiée directement par une archive IGN. SHA-256 **3aac9e8b979118b25df48e9ef21fc1029d735cc3c99a025cd1f5688560f41298**.
- [Contours administratifs data.gouv.fr](https://www.data.gouv.fr/datasets/contours-administratifs), millésime 2026, édition du **4 mai 2026**, produits généralisés à **100 m et 50 m**, principalement issus d'ADMIN EXPRESS de l'IGN pour les DROM.
- Contours 2026 à 100 m : SHA-256 **4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778**.
- Contours 2026 à 50 m : empreinte à figer à l'issue de la première exécution vérifiée.

**Les différentes généralisations de 2026 ne représentent pas des dates administratives différentes.** Elles permettent seulement une comparaison interne à une famille de produits du même millésime.

## Méthode

1. Vérifier l'intégrité et les codes INSEE des **22 communes de Guyane**, puis lire le WKT de la copie 2015.
2. Reprojeter les trois jeux de données en **EPSG:6933** et calculer leurs différences de surface et leurs indices de recouvrement.
3. Décomposer la différence d'emprise extérieure en composantes ; relever **l'aire**, un **point intérieur représentatif** et une **enveloppe rectangulaire approximative** (WGS84) pour les composants les plus significatifs de Régina, Sinnamary et Iracoubo.
4. Comparer les résultats 2015/2026 à 100 m et à 50 m, ainsi que **2026 à 100 m/2026 à 50 m**.
5. Contrôler les équations et la reproductibilité par tests, puis archiver **uniquement le rapport de métriques** dans GitHub Actions.

Les points et enveloppes sont des pistes de diagnostic : ils ne sont ni des bornes ni des contours administratifs, et ils ne permettent pas de déduire qu'une limite aurait effectivement changé entre les deux dates.

## Vérifications indispensables avant qualification

La localisation comme **littoral**, **cours d'eau frontalier** ou **limite interne** exige une source hydrographique ou côtière indépendante et datée. Le document de [nomenclature IGN](https://data.geopf.fr/annexes/ressources/documentation/Nomenclature_paquets.pdf) confirme le modèle de dénomination d'un paquet GEOFLA, **pas l'intégrité de la copie de 2015**. L'[API de téléchargement de l'IGN](https://www.data.gouv.fr/dataservices/api-geoplateforme-telechargement) est à explorer pour la recherche d'un exemplaire original ou d'un paquet officiellement conservé.

**Cet audit ne publie aucun polygone, ne valide aucune géométrie ancienne et ne modifie ni les 22 liens Pactols–COG approuvés pour 2026 ni les fiches historiques du référentiel Lieux.**

## Fichiers

Script : scripts/localiser_ecarts_geofla_guyane.py.

Tests : tests/test_localiser_ecarts_geofla_guyane.py.

CI : .github/workflows/lieux-guyane-localisation-ecarts.yml.

Rapport : artefact temporaire GitHub Actions, contenant des mesures, points représentatifs et enveloppes sans frontières publiables.
