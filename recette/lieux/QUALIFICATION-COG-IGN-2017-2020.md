# Qualification des couches IGN ADMIN EXPRESS COG 2017 et 2020

**Chantier Lieux — 16 novembre 2026 · PR de publication distincte · géométries datées**

## Deux dates distinctes par millésime

| Référentiel | Situation administrative Insee | Édition géométrique IGN |
|---|---|---|
| 2017 | COG au **1er janvier 2017** | `ADMIN-EXPRESS-COG_1-0__SHP__FRA_2017-06-19.7z`, **19 juin 2017** |
| 2020 | COG au **1er janvier 2020** | `ADMIN-EXPRESS-COG_2-1__SHP__FRA_2020-11-20.7z`, **20 novembre 2020** |

Il s'agit de deux éditions **vectorielles originales IGN**, et non de rendus WMS/WMTS. Une édition de géométrie produite en cours d'année ne doit pas être décrite comme une observation datée du 1er janvier : elle fournit une représentation associée à la composition COG du millésime, et son édition exacte est conservée en métadonnée.

Source IGN, API de découverte et de téléchargement : https://data.geopf.fr/telechargement/resource/ADMIN-EXPRESS-COG et https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/telechargement/.

Sources COG Insee : https://www.insee.fr/fr/information/2666684 et https://www.insee.fr/fr/information/4316069.

## Empreintes de source gelées

| Source | SHA-256 |
|---|---|
| IGN 2017 (50 721 560 octets) | `222c420c4edbbf6fac76a7426ff74f075feed337103794b5048ede92abcb0133` |
| IGN 2020 (160 935 924 octets) | `ff7a732872a069cbc31f426b613a751cf990e80f4a98e984ecd81d9adbf0fd08` |
| Insee régions 2017 | `5683ada3aa4691c70b50cd337a1f64a50913ab8fdabe2f87ddd1ffe0dca612ae` |
| Insee départements 2017 | `57feea872bd9e11be359e66430e79328123cb004a92195d9021daac749cdd18c` |
| Insee ensemble COG 2020 | `d63ef3b1b258b479839d6883ecc37385c850b0c8319d1efa0e982365e08054bf` |

## Contrôle des identités administratives

Les deux COG comportent **18 régions et 101 départements**. Leur comparaison entre 2017 et 2020 donne **zéro changement de code, zéro libellé régional ou départemental différent, et zéro changement de rattachement département–région**. Ces résultats ne sont pas transposés aux frontières sans examen géométrique.

## Géométries 2017

L'archive se répartit en un Shapefile métropolitain (Lambert-93) et cinq livraisons de DROM avec leurs projections locales. Les 18 régions et 101 départements ont été identifiés et comparés au COG 2017 : **aucune divergence de code, de libellé ni de rattachement**. La génération des deux GeoJSON à 100 m est **reproductible**.

Deux auto-intersections ont été corrigées sur copies de travail : **région 06 et département 976 à Mayotte**. Les rapports de production conservent la méthode `shapely.make_valid` et les écarts de surface ; **aucune géométrie invalide ne subsiste** dans les deux couches générées.

## Géométries 2020

L'archive est une livraison nationale au format Shapefile WGS84, avec des couches `REGION` et `DEPARTEMENT` distinguées de leurs variantes cartographiques. **Les 18 régions et 101 départements ont été validés contre le COG 2020** sans divergence de code, de nom ni de rattachement.

La génération des deux GeoJSON 2020 à 100 m a été effectuée deux fois à l'identique. **Aucune réparation topologique n'a été nécessaire**, et **aucune géométrie invalide ne subsiste**. Recette : [exécution IGN 2017/2020](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43887011910), réussie sur les deux matrices.

## Contrats de diffusion

- Conserver les archives brutes à leur URL IGN officielle et leurs empreintes.
- Attribuer les noms, codes et rattachements du COG Insee correspondant à chaque année.
- Publier seulement les polygones généralisés à 100 m et vérifiés comme valides, avec édition IGN et COG distincts.
- Rejeter toute modification de code inattendue et toute réparation topologique excessive ; consigner chaque correction.
- Maintenir les **103 correspondances Pactols–COG** PACA sans aucun nouvel alignement historique inféré.
- Ne pas modifier les géométries communales historiques (toujours non disponibles).

**Statut : recette des sources ; la publication effective doit suivre les tests Chromium et CI.**
