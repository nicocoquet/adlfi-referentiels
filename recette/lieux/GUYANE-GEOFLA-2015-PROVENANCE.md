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

## Bilan mesuré — comparaison de la copie 2015 avec 2026

La [première CI réussie n°43934919783](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43934919783) confirme :

- **22 entités communales** dans COMMUNE.shp, **22 codes INSEE explicites** et uniques sous l'attribut INSEE_COM, **22 géométries topologiquement valides** ;
- une seconde couche LIMITE_COMMUNE.shp (linéaire), conservée uniquement comme découverte de structure du paquet ;
- **22 comparaisons spatiales valides** avec la couche nationale 2026, calculées sur copies reprojetées vers EPSG:6933 ;
- une empreinte **SHA-256 de la copie tierce** : 3aac9e8b979118b25df48e9ef21fc1029d735cc3c99a025cd1f5688560f41298 ;
- un identifiant EPSG **non résolu automatiquement** par pyproj à partir du fichier PRJ, bien que le système source soit projeté et renseigné dans son WKT. La transformation et les comparaisons ont utilisé le WKT fourni, et non un EPSG inventé.

**Principaux écarts de superficie non recouvrante (différence symétrique) :**

| Code INSEE | Commune | Différence symétrique entre éditions | Jaccard |
| --- | --- | ---: | ---: |
| 97301 | Régina | 267,618 km² | 97,688 % |
| 97312 | Sinnamary | 159,664 km² | 87,404 % |
| 97303 | Iracoubo | 133,783 km² | 94,848 % |
| 97306 | Mana | 45,427 km² | 99,313 % |
| 97310 | Roura | 44,167 km² | 98,806 % |
| 97311 | Saint-Laurent-du-Maroni | 31,343 km² | 99,272 % |
| 97353 | Maripasoula | 28,909 km² | 99,845 % |
| 97305 | Macouria | 26,113 km² | 91,581 % |

Le **descriptif officiel IGN GEOFLA v2.2** [documente explicitement](https://geoservices.ign.fr/sites/default/files/2021-07/DC_GEOFLA_2-2.pdf) un allégement des géométries BD CARTO pouvant atteindre **1 000 m**, ainsi qu'un usage cartographique à petite échelle. Il serait donc incorrect d'interpréter directement les différences de surfaces observées comme des modifications juridiques des limites communales.

Cette mesure est **un progrès dans l'identification d'une source cartographique datée**, mais elle ne vaut **ni validation de la provenance originale IGN ni qualification des contours historiques**. Les différences fortes à Sinnamary et à Iracoubo appellent une inspection cartographique ciblée.

## Conditions avant utilisation dans le module Lieux

- retrouver la **provenance canonique IGN** et, si possible, l'empreinte de l'archive originale ;
- vérifier la **liste exacte des communes**, leur libellé et leur rattachement au COG correspondant au millésime de l'archive ;
- distinguer la **date d'édition GEOFLA**, la date de situation administrative annoncée et l'éventuelle actualité des limites ;
- documenter la précision GEOFLA et les opérations de reprojection/simplification ;
- comparer le tracé avec 2026 en tenant compte du décalage temporel et de la généralisation ;
- soumettre la publication des contours à une **validation cartographique distincte** des alignements Pactols–COG déjà approuvés.

**Aucun élément de cet audit n'autorise les frontières de 2015 à représenter 1993, 1976 ou 1969.** L'archive historique, si elle est confirmée et qualifiée, pourra constituer un candidat pour un **millésime cartographique explicite** dans le navigateur.

Cette analyse est réalisée après le lot de chronologie COG Guyane (PR 45) ; le sélecteur public reste Région / Département / Commune.
