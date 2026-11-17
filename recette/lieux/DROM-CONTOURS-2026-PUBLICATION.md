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

## Résultat de la recette réelle — 17 novembre 2026

La [CI DROM n°44183473837](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44183473837) est réussie et a versionné le GeoJSON de sortie dans la branche de PR.

- **129 géométries** toutes présentes, valides et datées 2026, réparties 971 : 32, 972 : 34, 973 : 22, 974 : 24 et 976 : 17 ; aucune réparation automatique ni géométrie historique.
- Les deux sorties sont identiques octet à octet : **484 150 octets**, SHA-256 **3f7553f1d397d0e66708381559ddc53e5b1e86239ca369565896**.
- Source géométrique : SHA-256 officiel de copie **4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778**.
- Vérifications : **DROM_129_INDEX_OK**, **DROM_129_NAVIGATEUR_OK**, **CORSE_360_NAVIGATEUR_OK**, **BFC_3614_NAVIGATEUR_OK**, **PDL_1140_NAVIGATEUR_OK**.
- L'index de recherche Pactols–COG reste distinct, et les anciens épisodes COG ne reçoivent aucun contour par inférence.

Les géométries des COM restent à instruire à part. Une seconde exécution de CI après versionnement devra confirmer l'état de branche avant fusion.
