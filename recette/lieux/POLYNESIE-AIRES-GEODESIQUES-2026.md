# Polynésie française — surfaces géodésiques des recouvrements ISPF

**17 novembre 2026 — PR de recette non validante, après PR 81.**

## Contexte
La PR 81 a établi **65 paires de polygones `Comas` ayant des intersections d'intérieur de superficie non nulle** : 44 paires d'unités fines appartenant à la même commune, 21 paires d'unités fines appartenant à des communes distinctes. Aucun recouvrement surfacique entre communes ni entre îles n'a été relevé.

## Méthode et référentiel
Le [CRS EPSG:4687 (RGPF)](https://epsg.io/4687) est géographique et utilise l'ellipsoïde **GRS 1980**. Les couches GeoJSON officielles de l'ISPF déclarent ce CRS. Pour obtenir des surfaces en mètres carrés sans imposer une zone UTM unique à l'ensemble des archipels, on utilise [`pyproj.Geod.geometry_area_perimeter`](https://pyproj4.github.io/pyproj/stable/api/geod.html), à partir de `pyproj.CRS.from_epsg(4687).get_geod()`.

`scripts/quantifier_recouvrements_ispf_polynesie.py` :

- consomme uniquement l'archive ISPF au SHA-256 **`6302ad2a17ec1fd8b51f70f1d8ba1501ee7ca212a9cd53c8df4221faedfe0b62`** ;
- réutilise les 65 paires identifiées dans l'audit PR 81, sans remplacer leur géométrie ;
- mesure les surfaces ellipsoïdales d'intersection **en m²**, en ne comptant que les composants polygonaux des `GeometryCollection` (lignes/points exclus) ;
- conserve la part de l'intersection relativement à chacune des deux unités fines, ainsi que par rapport à la plus petite ;
- classe toutes les paires par surface décroissante, en distinguant les 44 cas intra- et les 21 intercommunaux ;
- n'introduit **aucun seuil arbitraire** de gravité ou d'acceptation, et ne réalise aucune correction géométrique.

**Attention à l'interprétation des totaux :** la somme des 65 surfaces de paires peut compter plusieurs fois une zone commune à trois polygones ou davantage. Il ne s'agit donc pas nécessairement de la surface réelle unique en erreur. Les surfaces mesurées décrivent les données sources à leur millésime non encore qualifié, pas une limite légale.

## Contrôle indépendant et prochaines décisions

Le [jeu GEO PF de la Section Cadastre-Topographie](https://www.data.gouv.fr/datasets/geographie-administrative-de-la-polynesie-francaise) reste le candidat institutionnel à comparer. Sa structure, son CRS, son millésime exact et ses licences doivent être vérifiés dans un audit séparé. **Cette PR n'établit aucune concordance avec GEO PF.**

Avant de publier, contrôler les principaux recouvrements intercommunaux dans une deuxième source, qualifier la précision annoncée de chaque couche et isoler le cas des géométries historiques de Maria. La présence de polygones valides individuellement n'implique ni une mosaïque sans recouvrement ni une équivalence historique.

**Aucun contour diffusé, aucune autorité ou ARK ajouté.** Rapport JSON dans un artefact CI hors `docs/`.
