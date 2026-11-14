# Lieux AdlFI — Bourgogne-Franche-Comté : couverture XML et audit COG historique 2026

**14 novembre 2026 — PR n°24 — recette non validante.** Aucun alignement Pactols–COG nouveau ni contour historique n'est publié.

## 1. Sources et méthode de délimitation

L'inventaire de **736 ARK terminaux** est issu des trois fichiers nationaux précédemment contrôlés :

- `autorites_lieux.csv` : SHA-256 `878aa70f32d43313ea5bd36bbb30bbd6b57b4872ba2f68a5117ac6c35b6380b6` ;
- `occurrences_lieux.csv` : SHA-256 `b2e7332515c051e0c63e1fb29c840fa338aa85040fb2358a7df64d735b2942cd` ;
- `controle_concepts_pactols.csv` : SHA-256 `502db0f84188beca666d521417ad6775fb5f670c5b9a295250a9024fd4ede407`.

Le fichier de recette `inventaire-bourgogne-franche-comte.csv` (SHA-256 `efba75a28e0de837ef8832deff2ce5a5eb20e75132f3406e06cdc7ab6904fcad`) contient **736 ARK sans doublon**. Sa reconstruction reproduit exactement les 25 lignes du `lot-01-bourgogne-franche-comte.csv` sur leurs **21 champs**.

La sélection géographique est fondée sur la **hiérarchie Pactols** comportant Bourgogne, Franche-Comté ou Bourgogne-Franche-Comté. Un fichier éditorial appartenant à une autre région peut donc contenir une occurrence géographique BFC ; réciproquement, les lieux indexés dans un BSR de Bourgogne ne sont pas tous des lieux géographiques bourguignons.

## 2. Couverture XML : asymétrie liée à l’avancement éditorial

Dans les seules 1 885 occurrences reconnues comme BFC par la hiérarchie Pactols, les provenances éditoriales sont :

| Origine des XML | Fichiers distincts | Occurrences | Notices distinctes au sein du groupe |
| --- | ---: | ---: | ---: |
| Franche-Comté | **21** | **1 812** | **992** |
| Bourgogne | **2** | **20** | **13** |
| Autres corpus, dont Drassm | **21** | **53** | **29** |
| **Ensemble** | **44** | **1 885** | **1 034** |

Les fichiers de l'ancien ensemble Franche-Comté couvrent des éditions datées de **1992 à 2011**. Les deux fichiers Bourgogne retenus par l'extraction portent **tous deux sur 2009**. Le détail exhaustif des **44 chemins XML** et de leurs occurrences figure dans `couverture-xml-bfc-44.csv`.

| Département de la hiérarchie | ARK terminaux |
| --- | ---: |
| Côte-d'Or (21) | 13 |
| Doubs (25) | 231 |
| Jura (39) | 250 |
| Nièvre (58) | 3 |
| Haute-Saône (70) | 177 |
| Saône-et-Loire (71) | 28 |
| Yonne (89) | 2 |
| Territoire de Belfort (90) | 29 |
| Sans département (trois autorités régionales ou historiques) | 3 |
| **Total** | **736** |

**Interprétation rectifiée après précision du responsable éditorial (14 novembre 2026) :** la faible représentation de l'ancienne Bourgogne résulte **de l'avancement encore limité du travail de mise au format XML des notices d'opérations**. Il n'existe à ce stade **aucune preuve d'une anomalie de l'extracteur ni d'un déficit de fichiers XML pourtant disponibles et oubliés**. Les quatre départements de l'ancienne Bourgogne rassemblent 46 ARK (13 + 3 + 28 + 2), contre 687 dans les quatre départements de l'ancienne Franche-Comté ; trois autres ARK sont régionaux. Cette asymétrie est un **état de couverture documentaire du corpus AdlFI actuellement converti**, et non une propriété du territoire ou du thésaurus Pactols. Les résultats historiques portant sur les 736 ARK restent valables pour ce périmètre attesté, sans prétention à l'exhaustivité régionale. Aucun ARK ne doit être déplacé ou ajouté artificiellement pour rééquilibrer les chiffres.

## 3. Contrôle Pactols–COG 2026

Sources historiques Insee officielles : https://www.insee.fr/fr/information/8740222

- `v_commune_2026.csv` : `7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3` ;
- `v_commune_depuis_1943.csv` : `08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee` ;
- `v_mvt_commune_2026.csv` : `8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1`.

**Périmètre : 736 ARK, dont 727 possèdent une assertion Pactols vers un code de commune numérique.** Ces 727 assertions représentent **725 codes distincts** ; deux codes sont chacun déclarés sur deux ARK. Les neuf autres ARK concernent **trois autorités régionales** (Bourgogne, Franche-Comté, Bourgogne-Franche-Comté) et **six autorités départementales** : ce ne sont pas neuf alignements communaux « manquants ».

| Classe au COG 2026 | ARK |
| --- | ---: |
| Code `COM` actuel, même département que la hiérarchie Pactols | **670** |
| Code partagé `COM/COMD` au millésime 2026 | **10** |
| Code `COMA` (commune associée) | **10** |
| Code `COMD` (commune déléguée) | **12** |
| Code historique sans entrée au COG 2026 | **25** |
| Sans code communal numérique | **9** |
| **Total** | **736** |

La concordance du code et du département sur les 670 cas `COM` est un **contrôle de cohérence**, pas une validation de l'identité de l'ARK avec le COG.

Dédoublonnage : **807 périodes code–libellé distinctes**, **393 lignes de mouvements distinctes**, **975 états observés `TYPECOM/COM/LIBELLE`**. Les périodes de noms ne datent **pas** les géométries ; les mouvements ne constituent pas nécessairement autant d'actes administratifs uniques.

## 4. Dossiers prioritaires d'instruction

### Deux codes Insee partagés par deux ARK Pactols

- `25368` : **Marchaux** (`26678/pcrtHVMF65Ey3z`) / **Marchaux-Chaudefontaine** (`26678/pcrtPEJhK71UsV`).
- `25529` : **Sancey-le-Grand** (`26678/pcrtSYhbegbvSU`) / **Sancey** (`26678/pcrtqvgozFu6dO`).

Conserver quatre autorités Pactols. Le partage d'un code peut accompagner une création de commune nouvelle : il ne prouve pas une équivalence documentaire et ne constitue pas un critère de fusion.

### Vingt-cinq codes historiques absents du COG 2026

Ils se répartissent entre **Doubs : 9**, **Jura : 14**, **Haute-Saône : 1**, **Saône-et-Loire : 1**. Le tableau `codes-historiques-absents-bfc-25.csv` conserve pour chaque ARK les modalités et dates des mouvements, ainsi que les états avant/après, sans convertir automatiquement un ancien code en code actuel.

Exemples : **Chaudefontaine** (`25137`) rejoint Marchaux-Chaudefontaine en **2018** ; **Saint-Hymetière** (`39483`) est concerné par la commune nouvelle Saint-Hymetière-sur-Valouse en **2019** ; **Ciel** (`71131`) participe à la création de Verdun-Ciel en **2025**. Ces épisodes officiels doivent être documentés sans réattribuer les anciens ARK au contour 2026.

### Deux situations interdépartementales légitimes à conserver

- **Antorpe** : assertion Frantiq `39012` (Jura historique), désormais `COMA` rattachée à Saint-Vit (`25527`, Doubs).
- **Frettes** : assertion `52210` (Haute-Marne historique), désormais `COMA` rattachée à Champlitte (`70122`, Haute-Saône).

Ne pas « corriger » le préfixe de leurs codes par celui du département du parent actuel.

### Anomalie documentaire distincte

**Brain** (`21100`, Côte-d'Or) demeure une commune COG parfaitement réelle. Son indexation dans une notice *Pays de Retz / Autoroute A28* du corpus Pays de la Loire 2008 paraît suspecte au vu du contexte et pourrait impliquer **Brains** (`44024`), mais **aucune correction TEI ne peut être validée sans lecture de la notice**. L'alerte est distincte du dossier Béthon/Bethon.

### Instruction historique complémentaire vérifiée

Les **25 codes historiques** ont désormais été répartis en cinq profils à partir des **42 lignes de mouvements avant/après** : quatre fusions simples, douze rattachements par création/modification de commune nouvelle, sept suppressions ultérieures de statut délégué, une fusion-association transformée en fusion simple et un changement de nom suivi d'une commune nouvelle. Les deux codes partagés (`25368` et `25529`) et les communes associées **Antorpe** (`39012`) et **Frettes** (`52210`) ont fait l'objet de contrôles spécifiques.

Voir `INSTRUCTION-HISTORIQUE-EXCEPTIONS-BFC-20261114.md`, `scripts/instruire_exceptions_bfc_cog.py` et l'[exécution GitHub Actions réussie n°43628518269](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43628518269). Toutes les lignes restent des preuves administratives **non validantes** pour l'alignement des ARK.

## 5. Scripts, artefacts et publication

La branche contient :

- `docs/lieux/recette/inventaire-bourgogne-franche-comte.csv` ;
- `scripts/auditer_lieux_bfc_cog.py` ;
- `tests/test_auditer_lieux_bfc_cog.py` ;
- `.github/workflows/audit-lieux-bfc-cog2026.yml` ;
- trois tableaux d'instruction : couverture XML (44 fichiers), codes disparus du millésime courant (25), codes partagés entre ARK (2).

[CI BFC n°43625843444](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43625843444) : **réussie**, quatre tests réussis et sorties de recette archivées. Le serveur Insee ayant renvoyé HTTP 500, le workflow a repris **temporairement** une copie SHA-256 contrôlée de l'artefact Pays de la Loire du 14 novembre. **Cette copie expire le 16 novembre 2026** : elle n'est pas une solution permanente à l'indisponibilité de la source. L'accès Insee direct reste la voie nominale ; la procédure de secours devra être renouvelée ou remplacée.

Le rapport JSON et le graphe provisoire restent **des données de recette**, non des autorités historiques consolidées : aucun `skos:exactMatch` nouveau validé, aucune fermeture transitive des successions et aucune géométrie historique attribuée.

## 6. Arbitrages proposés pour la suite

1. **Avancement éditorial Bourgogne** : poursuivre progressivement la mise au format XML des notices d'opérations lorsqu'elles seront traitées, puis relancer l'extraction nationale et l'audit régional ; ne pas ouvrir d'audit d'anomalie de l'extracteur sans indice supplémentaire.
2. **Instruction historique BFC** : examiner d'abord les 25 anciens codes, les 10 entités `COMA`, les deux collisions d'ARK et les deux passages interdépartementaux, avant les 670 contrôles ordinaires.
3. **Structure des référentiels** : conserver les ARK documentaires et les états administratifs Insee comme identités de nature différente, avec type, intervalle, événement, preuve, puis géométrie millésimée distincte.
4. **Publication** : soumettre les rapprochements à la validation éditoriale avant toute modification de `docs/data/lieux*` ou de la carte publique.

**PR n°24 maintenue en brouillon.**
