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

Les mesures réelles seront consignées ici après exécution et vérification de la CI.
