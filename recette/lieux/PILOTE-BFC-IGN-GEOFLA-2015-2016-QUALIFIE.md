# Lieux AdlFI — qualification du pilote Bourgogne–Franche-Comté 2015/2016 par deux éditions originales IGN

**15 novembre 2026 · PR #31 · recette autonome, non publiée sur GitHub Pages.**

## Synthèse de la qualification

Les trois contours régionaux du pilote sont désormais obtenus **sans recours à Opendatasoft** :

| Période administrative (COG) | Région | Code | Origine du contour |
|---|---|---|---|
| État COG au 1er janvier 2015 | Bourgogne | `26` | Union des départements `21`, `58`, `71`, `89` de l'édition **GEOFLA IGN 2015-03-04** |
| État COG au 1er janvier 2015 | Franche-Comté | `43` | Union des départements `25`, `39`, `70`, `90` de la même édition |
| État COG au 1er janvier 2016 | Bourgogne-Franche-Comté | `27` | Union des huit départements de l'édition **GEOFLA IGN 2016-06-28** |

**Aucune couche régionale native n'est attribuée à l'IGN GEOFLA.** Les objets cartographiques sont des géométries construites par **union explicitement documentée des départements de la même édition**, non une union de départements 2026.

## Provenance vérifiée

| Édition | Référence et emplacement IGN | SHA-256 de l'archive téléchargée |
|---|---|---|
| GEOFLA 2.0 — 04/03/2015 | [GEOFLA département 2015](https://data.geopf.fr/telechargement/resource/GEOFLA/GEOFLA_2-0_DEPARTEMENT_SHP_LAMB93_FXX_2015-03-04) | `7831ad942f3c0646d7b9ebf9ba480dcf746d6f69d46834b38e36fa6681c1060e` |
| GEOFLA 2.2 — 28/06/2016 | [GEOFLA département 2016](https://data.geopf.fr/telechargement/resource/GEOFLA/GEOFLA_2-2_DEPARTEMENT_SHP_LAMB93_FXX_2016-06-28) | `8e1538791c12b7679ef0ffb638a0fc53f8e9dede359c170af6e15576826ea91a` |

Ces empreintes ont été calculées sur les fichiers téléchargés : elles sont **des contrôles locaux reproductibles et ne doivent pas être présentées comme des signatures publiées par l'IGN**.

La couche `DEPARTEMENT.SHP` a été vérifiée pour chaque édition : **96 départements métropolitains**, projection **EPSG:2154 / Lambert-93**, codes `CODE_DEPT` uniques et géométries valides. Le COG Insee des deux millésimes confirme les rattachements **26/43 → 27**. La distinction entre l'édition géographique de mars/juin et la date de référence COG au **1er janvier** est toujours affichée.

## Résultat de la comparaison SIG

Union des deux anciennes régions en 2015 comparée au contour de la nouvelle région en 2016, mesures en Lambert-93 :

| Mesure | Valeur |
|---|---:|
| Surface de l'union GEOFLA 2015 | **47 981,5778 km²** |
| Surface de l'union GEOFLA 2016 | **47 981,6093 km²** |
| Différence symétrique | **0,3602 km²** |
| Intersection / union (IoU) | **99,999249 %** |
| Hausdorff | **0,04986 km** |

Les huit départements ont été confrontés individuellement. Leurs taux de recouvrement sont supérieurs à **99,995 %**. Le faible écart n'atteste **aucune** modification juridique de frontière entre les éditions : il reflète la différence entre deux états de données géographiques (actualisation, simplification, ajustements).

Ce résultat est cohérent avec la réforme : la frontière externe de l'ensemble Bourgogne + Franche-Comté n'avait pas à changer lorsque ces deux régions ont fusionné, alors que la **limite administrative interne entre les deux régions a disparu** à partir du 1er janvier 2016.

## Chaîne reproductible et contrôle d'interface

- `scripts/reperer_geofla_2016_paquets.py` : inventaire des **119 sous-ressources** du catalogue officiel IGN et identification de l'unique paquet GEOFLA DÉPARTEMENT FXX/Lambert-93 pour 2016.
- `scripts/comparer_geofla_2015_2016_bfc.py` : vérification des archives, extraction des deux représentations, contrôle des codes régionaux et du rattachement des huit départements, comparaison de chaque département, export GeoJSON et rapport.
- `tests/test_comparer_geofla_2015_2016_bfc.py` : tests SIG, refus des appartenances 2015 appliquées à 2016, veto publication prématurée.
- `scripts/construire_vue_bfc_ign_2015_2016.py` : deux GeoJSON insérés dans un **HTML autonome**, fiches avec provenance des deux éditions.
- `.github/workflows/audit-lieux-geofla-departements-2016.yml` : téléchargement direct depuis la fiche catalogue, empreintes, tests, **deux générations des fichiers comparées octet à octet**, dépôt de l'artefact de recette.

[GitHub Actions, exécution spécialisée n° 43758735501](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43758735501) : **succès**.

**Contrôle local Chromium** du HTML issu de cette CI :
- situation 2015 : **deux chemins SVG**, titres Bourgogne et Franche-Comté ;
- situation 2016 : **un chemin SVG**, fiche Bourgogne-Franche-Comté `27` et liste de huit départements ;
- les deux fiches indiquent explicitement les sources IGN ;
- **aucune erreur JavaScript**.

Les données et le HTML ont été conservés dans l'artefact de CI, hors `docs/` et hors le site public. Aucune relation Pactols n'a été créée.

## Décisions et suite

**Qualification favorable du pilote géographique pour l'usage visé (cartographie historique régionale à échelle réduite)**, en gardant deux réserves :

1. Les millésimes **administratifs au 1er janvier** ne sont pas les dates des archives SIG **4 mars 2015** et **28 juin 2016**. Ne pas présenter les polygones comme témoins de chaque jour de ces années.
2. Les régions ont été reconstituées par unions de départements, ce qui doit être décrit dans la fiche de provenance.

**Prochain lot** : généraliser la chaîne aux **22 régions métropolitaines de 2015 et 13 de 2016**, valider la composition de tous les départements et les sept fusions, puis ajouter le choix d'échelon Région / Département. Les cinq DROM et les COMER feront l'objet de traitements cartographiques séparés en raison de leurs projections, statuts et géométries sources.

**Statut de la PR #31 : brouillon ; aucune publication Pages.**
