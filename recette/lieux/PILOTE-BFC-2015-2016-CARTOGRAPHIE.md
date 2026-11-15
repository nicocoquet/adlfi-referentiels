# Pilote cartographique Bourgogne – Franche-Comté (2015 / 2016)

**Référentiel Lieux · 15 novembre 2026 · PR #31 · pilote de recette, non publié sur Pages**

## Résultat obtenu et vérifications

Deux situations administratives distinctes sont désormais représentées par des **géométries fournies pour leurs millésimes propres**, avec restitution du code, du nom et de la composition départementale :

| Date de référence | Région | Code COG | Polygone issu de l'année | Nombre de sommets (géométrie source) |
|---|---|---|---:|---:|
| 2015-01-01 | Bourgogne | 26 | 2015 | 83 |
| 2015-01-01 | Franche-Comté | 43 | 2015 | 58 |
| 2016-01-01 | Bourgogne-Franche-Comté | 27 | 2016 | 113 |

Les géométries sont extraites de **[Régions et Collectivités d'Outre-Mer — Millésimé — France](https://public.opendatasoft.com/explore/dataset/georef-france-region-millesime/)**, jeu **réutilisé** produit par Opendatasoft, assemblant notamment des géométries IGN GEOFLA / ADMIN EXPRESS et comportant une forte simplification. **Ce n'est pas un export brut du GEOFLA 2015**. La source précise de chaque contour et le niveau de fidélité des limites au millésime restent à instruire avant toute publication de précision géographique élevée.

L'identité administrative et la composition des départements sont établies par les **COG Insee distincts 2015 et 2016**, rapprochés des tables départementales millésimées ; la loi du 16 janvier 2015 atteste la fusion au **1er janvier 2016**. Ces deux chaînes de preuve sont indépendantes. Les vues ne mélangent pas les deux années.

- En 2015, Bourgogne (`26`) comprend Côte-d'Or, Nièvre, Saône-et-Loire et Yonne. Franche-Comté (`43`) comprend Doubs, Jura, Haute-Saône et Territoire de Belfort.
- En 2016, Bourgogne-Franche-Comté (`27`) comprend les **huit départements**.
- La composition est **datée**, sans attribuer rétrospectivement le code 27 au millésime 2015.
- Les trois polygones sont issus de l'**API Opendatasoft Explore v2.1** et identifiés par `year`, `reg_code`, `reg_name`, `geo_shape`, contrôlés contre les codes COG. Le catalogue indique des millésimes commençant en 2015.
- La recette a parcouru **255 enregistrements** et ne conserve que **les trois couples (millésime, code) explicitement attendus**.

## Livrable et reproductibilité

1. `scripts/preparer_pilote_regions_bfc.py` : extraction contrôlée des **trois** géométries millésimées, sans fusion ni union de polygones de 2026.
2. `recette/lieux/pilote-bfc-modele.html` : interface autonome (deux boutons de date, carte vectorielle SVG, fiches régionales, source et limite de précision). Pas de dépendance JavaScript ou de service cartographique en ligne.
3. `scripts/construire_vue_bfc_2015_2016.py` : insertion contrôlée des deux GeoJSON dans un unique HTML transportable ; veto sur la publication accidentelle sous `docs/`.
4. `tests/test_preparer_pilote_regions_bfc.py` : noms et codes attendus, années distinctes, types géométriques, rejet d'une année manquante, exclusion d'une publication automatique.
5. `.github/workflows/audit-lieux-bfc-geometries.yml` : récupération des données, exécution des tests, deux générations du HTML comparées à l'octet, artefact conservé hors site public.

**CI spécialisée :** [exécution n° 43750179676](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43750179676) : succès.

**Contrôle navigateur local :** Chrome/Chromium testé sur le fichier HTML autonome, **2 surfaces cliquables en 2015**, **1 en 2016**, fiche de la nouvelle région fonctionnelle, **aucune erreur JavaScript**. La carte repose exclusivement sur les polygones embarqués.

**Statut :** `RECETTE_SOURCE_DERIVEE_A_QUALIFIER_NON_PUBLIEE`. **Zéro** nouveau lien Pactols, **zéro** géométrie historique fabriquée, **zéro** modification de `docs/`.

## Limites éditoriales et techniques

- Le géoréférencement et l'identification des régions sont cohérents avec le COG, mais la **précision du contour ODS simplifié** est insuffisante pour des analyses spatiales fines ou pour attester un détail frontalier. Le pilote documente un **millésime de représentation**, pas une assurance de délimitation parcellaire.
- **Millésime 2015 ou 2016 ne signifie pas une période de validité continue automatiquement attestée**.
- Ne pas extrapoler les polygones 2015 ou 2016 à 1943, 2000 ou 2026.
- Les versions **GEOFLA IGN** originales seront recherchées pour vérification, puis **ADMIN EXPRESS COG** pour les états actuels. Le rapprochement spatial des contours originaux et dérivés devra comprendre les différences de simplification et de projection.
- La page autonome est un prototype régional limité à deux années et au **niveau région**. Elle n'est pas encore la future interface commune « Zoom sur / Échelon territorial / Situation au ».

## Étape suivante

Éprouver le modèle avec les **sept fusions régionales** et leurs **65 départements dont le code de région change**, puis intégrer les noms provisoires et définitifs de 2016. Ensuite seulement, brancher les véritables sélecteurs de niveau régional/départemental/communal, puis les contours des arrondissements municipaux et les emprises ultramarines.
