# Polynésie française — préflight imagerie pour les cinq écarts de Hao (PR 88)

**17 novembre 2026 — recette non validante.** Suite à la PR 87.

## Objet

Les cinq principaux polygones de `GEO PF Hao 20200 - ISPF Ile 23` totalisent **6,463 km²** et sont localisés par des points intérieurs calculés dans la PR 87. L'objectif est de trouver une image d'observation de la Terre **effectivement acquise**, datée, géoréférencée, dont l'emprise recouvre ces cinq points et dont les conditions d'usage sont établies. La dénomination « motu », « récif » ou « lagon » reste non qualifiée.

## Deux filières documentaires

**Fonds polynésiens (DAF / Te Fenua).** La Direction des affaires foncières explique que la cellule Topographie produit des raster géoréférencés RGPF et que Te Fenua permet de consulter des superpositions d'images satellites et de cartes topographiques. Elle signale des droits spécifiques sur certaines images satellites et une diffusion soumise à contrat. Les pages institutionnelles ne fournissent pas, à elles seules, de métadonnées de **scène Hao** précisant date d'acquisition, résolution, footprint et licence. Il serait incorrect de lui assigner un millésime inventé ou de rediffuser une image affichée dans le portail.

Sources :
- [DAF, cellule Topographie — Nos services](https://www.service-public.pf/daf/cellule-topo_nosservices/)
- [DAF, cellule Topographie — Accueil](https://www.service-public.pf/daf/cadastre/cellule-topo_accueil/)

**Copernicus / Sentinel-2 L2A.** Le catalogue STAC du Copernicus Data Space Ecosystem dispose d'un point d'accès public documenté et des métadonnées par scène, incluant son horodatage d'acquisition et son empreinte. Les images Sentinel-2 L2A utilisent notamment **quatre bandes à résolution nominale de 10 m**. Les données Sentinel sont soumises aux conditions de réutilisation ouvertes propres au programme Copernicus ; ce n'est pas une permission automatique de republier une capture du service tiers.

Sources :
- [Documentation officielle STAC Copernicus Data Space](https://documentation.dataspace.copernicus.eu/APIs/STAC.html)
- [Description officielle de la mission Sentinel-2](https://dataspace.copernicus.eu/data-collections/copernicus-sentinel-missions/sentinel-2)
- [Conditions de réutilisation des données Sentinel](https://dataspace.copernicus.eu/terms-and-conditions)

## Protocole du préflight

Le script `scripts/inventorier_imagerie_hao_stac.py` interroge le catalogue public **`sentinel-2-l2a`** sur une emprise englobant les cinq points intérieurs PR 87, pour deux fenêtres de recherche **2022** (année de publication du paquet GEO PF) et **2025** (période récente). Ces fenêtres sont *des périodes de recherche*, et ne démontrent aucune relation entre une scène Sentinel-2 et le levé GEO PF.

Pour chaque produit renvoyé, le script conserve l'identifiant de scène, la date UTC d'acquisition, la plateforme, le taux de nuages **à l'échelle de la tuile** si disponible, l'emprise de la scène et les points PR 87 contenus dans sa géométrie STAC. Il refuse de déduire une couverture du seul rectangle englobant : un point doit être inclus dans la **géométrie réelle** de l'emprise. Si le catalogue est inaccessible, il enregistre explicitement un état `CATALOGUE_INACCESSIBLE_OU_INEXPLOITABLE` et ne fabrique pas une absence d'acquisition.

Il ne télécharge aucune bande raster ni ne traite des pixels : une scène dont le footprint couvre les cinq points peut rester entièrement nuageuse localement, présenter une qualité radiométrique insuffisante ou une géométrie inadaptée au trait de côte. Aucune date ni résolution propre aux cinq secteurs ne peut être considérée comme **validée** avant contrôle des fichiers et de leurs métadonnées.

## Limites et décision

Un taux de nuages à l'échelle d'une tuile ne constitue pas une mesure de la nébulosité **au point** ; la période et la précision de la source GEO PF restent non établies. Une résolution nominale de 10 m ne peut pas homologuer une limite administrative submétrique. Pour une qualification éditoriale, il faudra inspecter des extraits géoréférencés, décrire les classes d'objets sur l'image et, si possible, vérifier sur un autre fond topographique daté de précision connue.

**Statut : `RECETTE_NON_VALIDANTE`.** Résultats dans un artefact CI hors `docs/`, **aucune scène, image ou géométrie publiée**. Pas de correction d'autorité, de nom ou d'ARK.
