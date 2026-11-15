# Recette Lieux — comparaison BFC 2015, contours GEOFLA IGN et Opendatasoft

**15 novembre 2026 · PR 31 · qualification d'une source primaire, sans publication sur GitHub Pages**

## Découverte des archives officielles et discrimination des couches

L'API de téléchargement de la Géoplateforme IGN a été parcourue sur **toutes les pages du catalogue GEOFLA**. Elle propose 119 paquets, dont trois paquets métropolitains de la couche **DÉPARTEMENT**, datés respectivement du 4 mars, du 1er juillet et du 1er décembre 2015.

Le premier paquet tenté, **`GeoFLA_2-0__SHP_LAMB93_FXX_2015-03-04`**, ne contenait en réalité que la couche **CANTON**, malgré le nom générique du paquet. Il a été écarté pour la vérification des régions. Ceci justifie le contrôle systématique du **type d'objet extrait** et non du seul nom d'archive.

Le paquet effectivement retenu est le suivant :

- **Organisme producteur :** IGN.
- **Produit et édition annoncés :** `GEOFLA_2-0_DEPARTEMENT_SHP_LAMB93_FXX_2015-03-04`.
- **Fiche primaire vérifiée :** https://data.geopf.fr/telechargement/resource/GEOFLA/GEOFLA_2-0_DEPARTEMENT_SHP_LAMB93_FXX_2015-03-04
- **Téléchargement :** https://data.geopf.fr/telechargement/download/GEOFLA/GEOFLA_2-0_DEPARTEMENT_SHP_LAMB93_FXX_2015-03-04/GEOFLA_2-0_DEPARTEMENT_SHP_LAMB93_FXX_2015-03-04.7z
- **SHA-256 du fichier reçu :** `7831ad942f3c0646d7b9ebf9ba480dcf746d6f69d46834b38e36fa6681c1060e`.
- **MD5 du téléchargement :** non fourni par cette entrée du catalogue IGN ; **ne pas présenter le SHA-256 local comme une signature de l'IGN**.
- **Couche utilisée :** `DEPARTEMENT.SHP` (et non `LIMITE_DEPARTEMENT.SHP`).
- **Système de référence du fichier :** Lambert-93 (`EPSG:2154`).
- **Couverture inspectée :** 96 départements métropolitains, dont huit appartenant au futur ensemble BFC.

**Attention aux dates :** le COG 2015 documente l'état au **1er janvier 2015**, alors que cette livraison de géométrie est **étiquetée 4 mars 2015**. Même pour un millésime identique, ne pas affirmer que l'archive géométrique établit chaque limite précisément au 1er janvier sans preuve indépendante.

## Région et département : pas de couche GEOFLA régionale native

La documentation officielle de GEOFLA indique que le produit représente les communes, arrondissements et départements (et les cantons dans une ancienne édition), **mais ne comporte pas de couche indépendante de régions**.

En conséquence, les deux contours régionaux de référence sont une **reconstruction explicitement documentée, par union de départements issus de la même édition GEOFLA de 2015**, et non des polygones régionaux produits directement par l'IGN :

- **Bourgogne** : code régional `26`, départements **21 Côte-d'Or**, **58 Nièvre**, **71 Saône-et-Loire**, **89 Yonne** ;
- **Franche-Comté** : code régional `43`, départements **25 Doubs**, **39 Jura**, **70 Haute-Saône**, **90 Territoire de Belfort**.

Les huit fiches départementales du shapefile portent les **codes CODE_REG 26 ou 43**, concordants avec le COG Insee 2015. Les géométries sources et les deux unions sont géométriquement valides.

## Mesures : IGN 2015 vs ODS 2015

Les mesures ont été calculées en **Lambert-93**, à partir des deux régions reconstruites via GEOFLA et des polygones Opendatasoft à l'année 2015, tous reprojetés ou conservés dans le même système métrique.

| Région | Aire union IGN (km²) | Aire ODS (km²) | Différence symétrique (km²) | IoU | Distance de Hausdorff |
|---|---:|---:|---:|---:|---:|
| Bourgogne `26` | 31 701,21 | 31 727,64 | 710,85 | **97,78 %** | 5,293 km |
| Franche-Comté `43` | 16 280,37 | 16 301,87 | 424,31 | **97,43 %** | 4,103 km |

La **différence symétrique** correspond à la surface des zones appartenant à une seule des deux représentations. Elle **ne mesure pas** un transfert juridique de territoire. La source ODS est généralisée ; les écarts peuvent provenir des méthodes de généralisation et de l'origine des données.

Pour comparaison entre les deux représentations **ODS 2015 et ODS 2016**, l'union des anciennes régions atteint **99,781385 % de recouvrement** avec la nouvelle région en 2016, soit 105,1545 km² de différence symétrique ; cette concordance ne remplace **pas** une vérification IGN 2016.

## Statut et suite

**Choix de recette :** retenir l'union documentée des départements GEOFLA 2015 comme **source primaire pour la géométrie utilisée dans la vue 2015**, sous réserve explicite du changement entre **date de COG (1er janvier)** et **édition de géométrie (4 mars)**. Conserver ODS 2015 comme représentation simplifiée de comparaison. Le contour 2016 du pilote demeure un contour ODS millésimé 2016, dont la confrontation au GEOFLA 2016 original est **encore à mener**.

La PR 31 contient `scripts/qualifier_source_geofla_originale_bfc.py`, des tests de validité de source, et un workflow de recette téléchargeant, contrôlant et comparant les fichiers. L'archive d'entrée et les cartes de sortie sont conservées **hors `docs/`**. Aucune attribution automatique d'ARK Pactols et aucune géométrie historique construite à partir de contours 2026.

**Prochain jalon** : confronter le polygone BFC 2016 à la couche GEOFLA DÉPARTEMENT millésimée 2016, puis généraliser le principe aux sept fusions régionales avant d'ajouter le sélecteur « Échelon territorial ».
