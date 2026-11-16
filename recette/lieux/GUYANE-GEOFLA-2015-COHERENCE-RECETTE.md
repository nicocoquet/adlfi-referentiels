# Guyane — qualification complémentaire de GEOFLA 2015 et décomposition des écarts

**16 novembre 2026 — Recette non publiable ; source 2015 issue d’un miroir tiers.**

## Question résolue et question ouverte

Le premier audit a établi que la copie GEOFLA datée du **1er décembre 2015** contient **22 communes avec codes INSEE explicites**, 22 polygones topologiquement valides et deux couches distinctes COMMUNE / LIMITE_COMMUNE. Une comparaison surfacique avec les contours nationaux 2026 est possible, mais **elle ne démontre pas un changement administratif**.

La documentation IGN fournit désormais un contrôle indépendant de format :

- [IGN — référence géodésique RGFG95 / UTM 22N de la Guyane, EPSG:2972](https://geodesie.ign.fr/textes-et-decrets).
- [IGN — nomenclature des paquets GEOFLA communaux D973](https://data.geopf.fr/annexes/ressources/documentation/Nomenclature_paquets.pdf).
- [IGN — suivi de livraison des produits vecteur](https://geoservices.ign.fr/sites/default/files/2022-11/SE_DL_vecteur_3.pdf) : **GEOFLA passe en version 2.1 au 10 décembre 2015**, ce qui est cohérent avec la désignation du paquet étudié ; il ne s'agit pas d'une preuve de l'empreinte du fichier.
- [IGN — descriptif du produit GEOFLA v2.2](https://data.geopf.fr/annexes/ressources/documentation/DC_GEOFLA_2-2.pdf) : allégement géométrique jusqu'à 1 km **par rapport à BD CARTO**, non par rapport aux contours nationaux 2026, et usage cartographique proche de 1:1 000 000.

Le fichier [metadata.txt du miroir de l'archive](https://github.com/justinelliotmeyers/official_france_administrative_boundary_shapefile/blob/master/metadata.txt) attribue lui-même les données à **IGN** et à l'ancien domaine professionnels.ign.fr. C'est une **déclaration du miroir**, pas une attestation d'intégrité ou de version officielle.

**À ce stade, aucune archive 2015 canonique IGN ni empreinte originale vérifiable n'a été retrouvée.** Ne pas employer le terme « source authentifiée » dans le site.

## Complément d'audit

L'évolution du script scripts/auditer_geofla_guyane_2015.py contrôle en plus :

1. si le WKT du fichier PRJ **équivaut effectivement** au système EPSG:2972, même si l'EPSG n'est pas restitué automatiquement ;
2. si les centres des 22 polygones transformés en WGS84 restent dans le **domaine géographique attendu de Guyane** ;
3. si les **unions des 22 communes**, pour 2015 et 2026, sont valides ;
4. l'**écart symétrique des emprises totales** 2015–2026, pour séparer le désaccord externe du cumul des désaccords par communes ;
5. les **surcomptages de surface** (somme des aires communales moins aire de leur union), qui signaleraient d'éventuels recouvrements entre communes de même millésime.

Il s'agit de métriques de diagnostic. Le fait qu'un écart d'emprise soit inférieur au cumul des écarts communaux est compatible avec des différences à l'intérieur du maillage communal, **sans établir leur cause**.

Les métriques sont calculées en EPSG:6933 sur géométries projetées depuis le **WKT effectivement livré**, jamais depuis le code EPSG supposé. On ne compare pas les valeurs brutes exprimées dans les projections différentes.

## Protocole de classement des écarts

**Première priorité** : Sinnamary (97312), Iracoubo (97303) et Régina (97301), puis les autres communes où le recouvrement de Jaccard est réduit.

Il faut vérifier si les écarts portent essentiellement sur :
- les bords externes (littoral, fleuves frontaliers, îles) ;
- les séparations internes entre communes ;
- les effets du changement de précision, d'échelle, d'agrégation ou de traitement géométrique ;
- les éventuelles décisions administratives datées, **seulement lorsqu'un texte ou un mouvement COG les atteste**.

La somme des différences symétriques par commune ne représente pas directement une surface de territoire modifié : une même bande peut contribuer à plusieurs différences à l'intérieur du découpage.

## État éditorial

Les **22 identifiants Pactols ↔ COG 2026** sont validés et ne sont pas modifiés par cette analyse. Les **quatre autorités historiques** et les événements de 1969, 1976, 1989 et 1993 sont documentés séparément.

**Aucun contour GEOFLA n'est adopté pour le millésime 2015** tant que la provenance n'est pas suffisamment attestée. Aucune géométrie 2015 ou 2026 n'est inférée pour une année antérieure ; aucune modification de docs/ n'est autorisée dans ce lot.

Les résultats sont conservés dans un rapport GitHub Actions avec SHA-256 de l'archive tierce et du contour national 2026.
