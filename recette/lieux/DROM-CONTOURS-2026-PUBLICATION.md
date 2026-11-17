# DROM — publication des contours communaux 2026 (129 communes)

**17 novembre 2026 — chantier géométrique séparé des autorités Pactols, issue #105.**

## Sources et bornes

Le jeu Etalab/IGN « Contours administratifs » édition **4 mai 2026**, généralisation **100 mètres**, est consulté depuis l'URL officielle :
https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2026/geojson/communes-100m.geojson.gz

Source géométrique épinglée SHA-256 : `4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778`.
COG Insee au **1er janvier 2026**, `v_commune_2026.csv` SHA-256 `7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3`.

La jointure exige `TYPECOM=COM`, code INSEE, département égal au préfixe et région COG correcte. Effectifs : Guadeloupe 32, Martinique 34, Guyane 22, La Réunion 24, Mayotte 17, soit **129 communes**.

## Principes et exclusions

La géométrie source de chaque commune doit être Polygon ou MultiPolygon **non vide, valide topologiquement**, en coordonnées WGS84 et d'aire positive. Les doublons, omissions ou changements de source interrompent la génération. Aucune réparation automatique.

Le GeoJSON de sortie est indépendant de `recherche-2026.json`. Aucun nouvel ARK Pactols n'est créé, aucune limite ancienne n'est reconstruite. Les polygones sont cliquables vers les fiches COG 2026 ; la frise antérieure ne permet leur affichage que comme repère moderne optionnel et daté.

Hors périmètre : Saint-Pierre-et-Miquelon (2), Nouvelle-Calédonie (33) et Polynésie française (48). Les anomalies Tahaa (98745) et Dumbéa (98805) restent en instruction.

## Qualification technique

La CI dédiée régénère le fichier deux fois, vérifie les SHA, les 129 codes et les géométries Shapely ; réalise les tests Node et Chromium sur cinq DROM ainsi que les non-régressions Corse/BFC/PDL. Le GeoJSON est commité sur la branche de PR seulement après réussite.