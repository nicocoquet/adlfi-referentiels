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
