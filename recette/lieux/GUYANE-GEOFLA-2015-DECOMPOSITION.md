# Guyane — écarts de limites : contour extérieur et maillage intercommunal

**16 novembre 2026 · Audit cartographique non validant et non publiable.**

## Objet

L'audit initial a mesuré, sur des géométries reprojetées en EPSG:6933, **733,434981 km² de différence symétrique entre les emprises totales** GEOFLA édition 2015 et contours nationaux édition 2026, mais **918,066563 km² lorsque les 22 différences par code sont additionnées**. Il faut expliquer cette différence arithmétique sans confondre les changements de *dessin cartographique* et les événements administratifs.

## Décomposition mathématique

Deux partitions de 22 unités, A (copie GEOFLA 2015) et B (contours nationaux 2026) sont comparées à **codes INSEE identiques**. Le calcul contrôle en préalable la validité des polygones, l'absence de recouvrement entre communes du même millésime et l'absence d'objet manquant.

- **Écart d'emprise externe** : surface de `Union(A) Δ Union(B)`, soit les portions représentées dans un millésime mais pas dans l'autre.
- **Écart interne unique** : surface pour laquelle le dessin de 2015 attribue un code communal et celui de 2026 en attribue un autre, à l'intérieur de l'emprise commune.
- **Cumul des écarts par commune** : **écart externe + 2 × écart interne**, car une zone passant du code i au code j est comptée une fois comme disparition pour i et une fois comme apparition pour j.

L'égalité n'est valable qu'après vérification du comportement en partition (pas de recouvrements mesurables). La CI bloque les surfaces si cette égalité ne se ferme pas.

**Attention :** « passage du code i vers le code j » indique une **différence d'affectation des surfaces entre deux représentations géométriques**. Cela **n'établit pas** une cession administrative, une fusion, ni un changement juridique effectif entre 2015 et 2026.

## Trois secteurs prioritaires

- **Régina — 97301** : écart cumulé mesuré précédemment 267,618413 km².
- **Sinnamary — 97312** : écart cumulé 159,664326 km², Jaccard 87,40 %.
- **Iracoubo — 97303** : écart cumulé 133,782800 km².

Pour chacun, le rapport JSON de recette distingue :
- la partie présente en 2015 mais hors de l'emprise collective de 2026 ;
- la partie présente en 2026 mais hors de l'emprise collective de 2015 ;
- les parties de l'emprise commune affectées à un autre code entre les deux jeux ;
- les codes des communes voisines impliqués dans ces différences d'affectation.

L'expertise suivante devra rapprocher ces observations des **zones hydrographiques, côtières ou frontalières** et des sources originales des deux produits. Les positions des écarts ne sont **pas** automatiquement qualifiées en littoral ou en frontière.

## Provenance et limites

Copie GEOFLA 2015 depuis un miroir GitHub, SHA-256 `3aac9e8b979118b25df48e9ef21fc1029d735cc3c99a025cd1f5688560f41298` ; produit IGN **probable mais non authentifié** par comparaison avec un exemplaire original. La documentation [GEOFLA IGN](https://www.data.gouv.fr/datasets/geofla-r) précise la vocation cartographique généralisée de la série. La documentation officielle du produit indique que la donnée GEOFLA peut avoir une ancienneté maximale d'un an à la date de l'édition : le nom « 2015 » ne suffit pas à déterminer la date d'effet des limites. <https://geoservices.ign.fr/sites/default/files/2021-07/DC_GEOFLA_2-2.pdf>

Les contours 2026 sont des [contours administratifs nationaux diffusés par Etalab](https://www.data.gouv.fr/datasets/contours-administratifs) : source, méthodologie et généralisation **différentes**. Une différence de contour peut provenir de cette diversité et non d'un événement communal.

## Livrables techniques

Le script `scripts/auditer_geofla_guyane_2015.py` ajoute une structure `decomposition_ecarts_cartographiques` à son rapport de recette existant. Les tests synthétiques vérifient une partition de 22 géométries avec une bande externe et un décalage de frontière interne, puis refusent une partition incomplète ou des recouvrements entre communes.

La CI spécialisée contrôle les métriques et archive **uniquement le rapport chiffré**, sans polygones ni tracés de différences. Aucun ajout de limite cartographique sous `docs/` ; les 22 relations Pactols–COG 2026 validées sont maintenues.
