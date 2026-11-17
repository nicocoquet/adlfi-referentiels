# Saint-Pierre-et-Miquelon — publication contrôlée des deux contours communaux 2026

**17 novembre 2026 — tranche géométrique autonome, issue #105.**

## Portée des données

Communes COG/COMER au 1er janvier 2026 :
- **97501 Miquelon-Langlade**, correspondance Pactols déjà approuvée : `26678/pcrtQAMzeGHldU`.
- **97502 Saint-Pierre**, correspondance Pactols déjà approuvée : `26678/pcrtYQmFfwxLq8`.

Le référentiel détient déjà leurs fiches, ARK et chronologies COG. Cette PR ajoute uniquement leurs **géométries de référence 2026**, et ne modifie aucune correspondance Pactols, mouvement ou épisode historique.

Source cartographique : `https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2026/geojson/communes-100m.geojson.gz` ; édition **4 mai 2026**, généralisation **100 m** ; SHA-256 du paquet `4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778`. L'identification des deux communes est contrôlée contre le référentiel COG/COMER 2026 versionné dans `docs/data/lieux-outremer/recherche-2026.json`, dont le lot probatoire possède son propre SHA d'audit.

## Qualification limitée

Les deux polygones sont non vides, valides au sens GEOS, dans l'emprise géographique de l'archipel et sans recouvrement géométrique notable. Les géométries sources sont conservées **sans réparation ni modification des coordonnées**.

**Une géométrie Etalab valide topologiquement n'est pas une limite juridiquement homologuée**, ni un tracé datable des périodes COG anciennes. Pour 2026, les contours sont cartographiés avec mention de la provenance. Hors de 2026, ils restent seulement disponibles comme **repères contemporains optionnels en tirets**, à la demande de l'utilisateur.

## Mise en ligne et non-régressions

La CI reconstruit deux GeoJSON identiques octet à octet, contrôle la provenance et les deux codes, les géométries Shapely, puis les fiches et zooms dans Chromium. Elle préserve les tests sur les 129 DROM, la Corse, la BFC et les Pays de la Loire.

Le GeoJSON est versionné dans la branche de la PR seulement **après réussite**. Les limites de Polynésie et de Nouvelle-Calédonie, notamment les anomalies Tahaa/Dumbéa, demeurent séparées dans l'audit PR #109.

Le contenu de l'index des identifiants Pactols reste inchangé. Aucune commune associée ou structure juridique COMER n'est créée ou renommée par déduction de la carte.
