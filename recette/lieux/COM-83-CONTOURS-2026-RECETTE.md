# 83 communes des COM : recette géométrique préalable (2026)

**17 novembre 2026. Après publication des 129 DROM (PR #107).**

La couverture du moteur de recherche COG contient aussi 83 communes des trois espaces : Saint-Pierre-et-Miquelon (975, 2), Polynésie française (987, 48) et Nouvelle-Calédonie (988, 33).

L'audit examine le GeoJSON national Etalab/IGN du 4 mai 2026, à la généralisation 100 m (SHA-256 `4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778`), mais ne diffuse **aucune géométrie**.

## Pourquoi la validité topologique ne suffit pas

- L'index public signale déjà Tahaa (98745) et Dumbéa (98805) comme présentant des géométries invalides.
- En Polynésie, les sources ISPF et GEO PF ne se recouvrent pas toujours, et leurs conventions de découpage et de date doivent être approfondies.
- Dans les COM, le fond Etalab peut résulter en partie de données OSM ; son validateur GEOS n'établit pas la qualité juridique de la limite.

La CI réalise deux contrôles identiques, dénombre les polygones présents et topologiquement valides et fournit un rapport JSON. Aucun ARK Pactols, aucun contour historique et aucune relation d'identité ne sont créés.

Après la recette, privilégier une publication **par territoire et par source qualifiée**, sans réparer silencieusement les polygones invalides ni assimiler les communes associées ISPF aux communes principales COG.


## Résultats contrôlés (17 novembre 2026)

[Workflow n°44184688677](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44184688677) **réussi** : 83 géométries présentes, **81 valides** au contrôle GEOS et deux invalides, avec deux rapports JSON identiques. Zéro contour ou ARK publié.

| Territoire | Communes COG | Géométries présentes | Valides GEOS | Invalides |
| --- | ---: | ---: | ---: | ---: |
| Saint-Pierre-et-Miquelon (975) | 2 | 2 | 2 | 0 |
| Polynésie française (987) | 48 | 48 | 47 | 1 |
| Nouvelle-Calédonie (988) | 33 | 33 | 32 | 1 |
| **Total** | **83** | **83** | **81** | **2** |

- **Tahaa (98745)** : multi-polygone à auto-intersection GEOS vers **longitude –151,447423 ; latitude –16,564923**.
- **Dumbéa (98805)** : multi-polygone à auto-intersection GEOS vers **longitude 166,4384 ; latitude –22,1726**.

Les diagnostics coïncident avec les deux signalements déjà présents dans le manifeste de recherche COG ultramarin. Les coordonnées sont des **points diagnostiques d'auto-intersection du dessin**, pas des limites juridiquement qualifiées.

**Suite éditoriale proposée** : étudier d'abord la publication des deux contours de Saint-Pierre-et-Miquelon comme repères **Etalab 2026** clairement attribués, puis séparer les dossiers Polynésie et Nouvelle-Calédonie selon les sources et les anomalies ; ne pas inférer une homologation administrative de la seule topologie GEOS.
