# Guyane — audit de provenance et de géométrie GEOFLA, paquet 2015

**16 novembre 2026 · Recette documentaire, aucune publication cartographique.**

## Question

Peut-on retrouver une édition de **contours communaux de Guyane antérieure au contour national 2026**, pour faciliter l'instruction des périodes historiques (en particulier après 1993) sans substituer des géométries contemporaines aux limites anciennes ?

## Paquet candidat identifié

**GEOFLA_2-1_COMMUNE_SHP_UTM22RGFG95_D973_2015-12-01.rar**, dans l'[inventaire public d'une copie tierce d'archives de données administratives françaises](https://github.com/justinelliotmeyers/official_france_administrative_boundary_shapefile). Ce fichier est référencé dans les métadonnées GitHub sous une taille de **103 109 octets** (taille de l'archive, non celle du shapefile décompressé).

Sources de qualification :
- [IGN — Nomenclature des paquets de données](https://data.geopf.fr/annexes/ressources/documentation/Nomenclature_paquets.pdf), où sont documentés les codes de produit GEOFLA et la projection UTM22 RGFG95 de Guyane.
- [IGN — GEOFLA sur data.gouv.fr](https://www.data.gouv.fr/datasets/geofla-r) : source institutionnelle du produit, arrêté puis remplacé par ADMIN EXPRESS.
- [Insee — COG et évolution des communes](https://www.insee.fr/fr/information/2560452).

**Cette copie n'a pas encore été rapprochée d'une archive IGN originale ou d'une empreinte officielle.** Elle doit être qualifiée comme **SOURCE TIERS — NON AUTHENTIFIÉE**. Son nom de fichier ne suffit pas à démontrer la date de validité des frontières ni l'exactitude de ses objets.

## Audit en lecture seule

Le script scripts/auditer_geofla_guyane_2015.py et le workflow .github/workflows/lieux-guyane-geofla-2015-recette.yml :

1. téléchargent le seul paquet candidat identifié, en conservent le SHA-256 et vérifient la structure des chemins d'archive ;
2. détectent le shapefile, son schéma attributaire, son système de référence et les **codes INSEE explicitement présents** dans ses champs ;
3. inventorient les entités, la validité topologique et les codes du département 973 ;
4. comparent les **surfaces et intersections** dans une même projection équivalente EPSG:6933 avec le fichier national 2026 déjà contrôlé ;
5. exportent **uniquement un rapport de métadonnées et mesures**, sans géométries ni polygones de différence.

Les différences peuvent refléter des **méthodes de généralisation** différentes, des corrections cartographiques, des variations de résolution ou d'autres traitements. **Elles ne permettent pas à elles seules de qualifier des changements de limites administratives.**

Le contrôle doit échouer plutôt que d'inventer un code à partir d'un toponyme ou de supposer un système de coordonnées. Une divergence dans deux champs de code INSEE est traitée comme ambiguë.

## Conditions avant utilisation dans le module Lieux

- retrouver la **provenance canonique IGN** et, si possible, l'empreinte de l'archive originale ;
- vérifier la **liste exacte des communes**, leur libellé et leur rattachement au COG correspondant au millésime de l'archive ;
- distinguer la **date d'édition GEOFLA**, la date de situation administrative annoncée et l'éventuelle actualité des limites ;
- documenter la précision GEOFLA et les opérations de reprojection/simplification ;
- comparer le tracé avec 2026 en tenant compte du décalage temporel et de la généralisation ;
- soumettre la publication des contours à une **validation cartographique distincte** des alignements Pactols–COG déjà approuvés.

**Aucun élément de cet audit n'autorise les frontières de 2015 à représenter 1993, 1976 ou 1969.** L'archive historique, si elle est confirmée et qualifiée, pourra constituer un candidat pour un **millésime cartographique explicite** dans le navigateur.

Cette analyse est réalisée après le lot de chronologie COG Guyane (PR 45) ; le sélecteur public reste Région / Département / Commune.
