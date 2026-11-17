# Mayotte — recette géométrique GEOFLA 2015 / Etalab 2026

**17 novembre 2026 — audit cartographique non validant, sans diffusion de polygones.**

## Contexte documentaire

La [PR n°61](https://github.com/nicocoquet/adlfi-referentiels/pull/61) documente les **17 codes communaux** de Mayotte depuis l'ouverture de la série COG COMER en 2007, puis leur passage à la série DROM le **31 mars 2011**, avec les **16 correspondances Pactols–COG validées pour 2026** et l'ARK **Dembeni 97607** confirmé mais non aligné.

La comparaison géométrique **GEOFLA 2015 / Etalab 2026** intervient **après** la transition de 2011. Elle ne peut par construction restituer ni les limites communales antérieures à 2011, ni prouver le périmètre de la collectivité de Mayotte en 2007.

## Provenance des deux produits

- Archive candidate : `GEOFLA_2-1_COMMUNE_SHP_RGM04UTM38S_D976_2015-12-01.rar`, issue du [miroir documentaire GitHub tiers](https://github.com/justinelliotmeyers/official_france_administrative_boundary_shapefile) ; **l'authenticité de la livraison IGN originale n'est pas établie**.
- Projection **attendue** : `RGM04 / UTM zone 38S`, **EPSG:4471**, mentionnée dans la [documentation IGN NUALID](https://data.geopf.fr/annexes/ressources/documentation/DC_NUALID_1-0.pdf). Elle devra être confrontée au WKT du PRJ de la source, sans supposition issue du nom de l'archive.
- Référence nationale : [Etalab / IGN, contours administratifs 2026](https://www.data.gouv.fr/datasets/contours-administratifs), éditions à **100 m** et **50 m** (source 2026-05-04). Empreintes SHA-256 déjà contrôlées : `4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778` et `6db43cd98a7211516da64e91761100504ba3feeddc986ebe0d50f84df624cd38`.

## Protocole

1. Inventorier la copie candidate, mesurer le SHA-256 réel, lire les SHP/PRJ, vérifier le CRS, les géométries et les **17 codes attributaires INSEE**.
2. Établir les partitions spatiales de 2015 et 2026 dans un système équivalent surfacique (**EPSG:6933**).
3. Vérifier les topologies et l'absence de recouvrement intercommunal.
4. Comparer GEOFLA 2015 aux deux généralisations Etalab 2026, et comparer les deux généralisations d'une même année entre elles.
5. Décomposer la différence cumulée des communes en **écart d'emprise extérieure + deux fois l'écart interne unique**, vérifier la fermeture de cette équation à partir des géométries non arrondies.
6. Localiser les principales composantes de différence par un **point intérieur représentatif**, sans publier le contour correspondant.
7. Répéter l'audit deux fois et comparer les rapports JSON octet par octet ; archiver uniquement le rapport numérique.

**Inventaire engagé.** Les métriques seront ajoutées uniquement une fois calculées et contrôlées.

## Interprétation

La généralisation GEOFLA et les versions Etalab peuvent différer sur le trait de côte, les limites intercommunales et les choix de représentation indépendamment de toute évolution légale. Aucune ligne de résultat ne sera interprétée comme un mouvement administratif sans texte officiel ou autre source historique qualifiée.

**Aucun nouveau contour historique, alignement Pactols, ou relation de succession n'est produit ; aucune modification sous `docs/`.**
