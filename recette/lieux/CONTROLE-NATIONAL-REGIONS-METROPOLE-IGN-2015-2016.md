# Lieux AdlFI — 35 contours régionaux métropolitains GEOFLA 2015/2016

**16 novembre 2026 — PR #31 (brouillon) — recette technique, hors GitHub Pages.**

## Périmètre et principe

La production utilise les **deux éditions originales** de la couche `DÉPARTEMENT` d'IGN GEOFLA en Lambert-93 (EPSG:2154) :

- GEOFLA 2.0, édition du **4 mars 2015** : `GEOFLA_2-0_DEPARTEMENT_SHP_LAMB93_FXX_2015-03-04` ; SHA-256 archive `7831ad942f3c0646d7b9ebf9ba480dcf746d6f69d46834b38e36fa6681c1060e`.
- GEOFLA 2.2, édition du **28 juin 2016** : `GEOFLA_2-2_DEPARTEMENT_SHP_LAMB93_FXX_2016-06-28` ; SHA-256 archive `8e1538791c12b7679ef0ffb638a0fc53f8e9dede359c170af6e15576826ea91a`.

Pour chaque édition, la géométrie régionale est calculée par **union des polygones départementaux de cette même édition**, regroupés exclusivement d'après le code régional attesté par le **COG Insee de la même année**. Aucune limite de 2026 n'intervient. Les noms proviennent du tableau régional COG correspondant, pas d'un référentiel de dénominations modernes.

Résultat attendu : **22 régions métropolitaines de 2015**, **13 régions métropolitaines de 2016**, soit **35 géométries dérivées**. Cette procédure ne produit **pas** de couche régionale « originale IGN » : ce sont des unions calculées sur une source IGN départementale.

## Verrous et contrôles

Le script `scripts/construire_regions_metropole_geofla_2015_2016.py` :

1. Vérifie les empreintes SHA-256 des deux archives IGN et des **quatre** fichiers INSEE `reg/dept` 2015/2016.
2. Exige 96 départements par édition, des codes uniques, des géométries valides et le CRS EPSG:2154.
3. Exige la concordance des rattachements `CODE_DEPT / CODE_REG` IGN avec `DEP / REGION` COG, pour chaque édition.
4. Regroupe les départements par région, vérifie les **65 changements** de code, les **sept fusions** et **six continuités** et contrôle la **composition départementale inchangée** des 13 régions successeures.
5. Compare pour chacune des 13 régions le contour extérieur 2015 (union des prédécesseurs, éventuellement plusieurs) au contour 2016, avec aire, intersection/union, différence symétrique et distance de Hausdorff en projection métrique. Un recouvrement inférieur à 99 % interrompt l'audit : c'est un garde-fou **technique**, pas un critère historique d'identité.
6. Convertit le résultat en GeoJSON WGS84 pour la seule recette, sans modifier `docs/`.
7. Exécute deux productions identiques et vérifie que les quatre exports sont **identiques à l'octet**.

## Livrables de recette

Dans l'artefact du workflow `.github/workflows/audit-lieux-geofla-departements-2016.yml` :

- `regions-metropole-2015-IGN-geofla.geojson` (22 entités).
- `regions-metropole-2016-IGN-geofla.geojson` (13 entités).
- `comparaisons-regions-metropole-IGN-2015-2016.csv` (13 rapprochements, dont 7 fusions).
- `rapport-regions-metropole-IGN-2015-2016.json` (cardinalités, métriques, empreintes et réserves).

Les noms COG 2015 et 2016 sont des **noms datés** : en particulier, `Centre` est le libellé de référence du 1er janvier 2015 avant l'entrée en vigueur de `Centre-Val de Loire` le 17 janvier ; plusieurs dénominations provisoires du 1er janvier 2016 deviennent définitives le 30 septembre 2016. Les événements juridiques figurent dans l'audit de la hiérarchie et ne doivent pas être déduits du seul libellé inscrit dans ces GeoJSON.

## Réserves et suite

- **Date administrative différente de la date SIG** : les COG décrivent une situation au 1er janvier ; les géométries GEOFLA sont datées de mars et de juin. Aucune continuité de validité n'est affirmée entre ces dates.
- Les petites différences entre les contours 2015/2016 sont des **écarts de représentation** entre éditions ; elles ne démontrent pas des mutations de limites administratives.
- Les **cinq départements ultramarins** sont hors du périmètre `FXX` et doivent recevoir leurs propres sources de géométrie, dans la suite du projet, sans confondre DROM et COMER.
- Les **régions BSR/AdlFI** restent des autorités éditoriales distinctes de l'appartenance régionale COG. Aucun alignement automatique Pactols.
- **Ne pas publier** les 35 contours dans le module Lieux avant recette de l'interface « Zoom sur », « Échelon territorial », « Situation au » et de la provenance affichée.

Statut des mesures nationales : **à confirmer sur le workflow associé à ce commit**. Aucun pourcentage spatial national n'est annoncé avant la réussite du traitement intégral.
