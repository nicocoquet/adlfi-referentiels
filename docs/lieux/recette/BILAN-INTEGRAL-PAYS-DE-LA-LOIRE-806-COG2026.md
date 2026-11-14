# Lieux — Pays de la Loire : audit régional complet, 806 ARK et COG historique 2026

**14 novembre 2026 — PR n°24 — recette technique et scientifique non validante.**

L'inventaire national Pactols–XML a été rapproché des trois fichiers Insee officiels du COG 2026. Tous les fichiers sources sont vérifiés par empreinte SHA-256 ; le même audit complet a réussi dans le [workflow GitHub Actions n°43611387949](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43611387949). Les sorties sont dans l'artefact `audit-lieux-pays-de-la-loire-806-cog2026`.

## Périmètre et qualification

| Contrôle | Résultat |
| --- | ---: |
| ARK Pactols terminaux observés dans les chaînes XML AdlFI de la région | **806** |
| ARK avec un code communal numérique dans l'assertion SKOS Frantiq | **797** |
| Codes numériques Insee distincts assertés | **775** |
| Codes partagés entre deux ARK Pactols différents | **22** |
| ARK sans code communal numérique exploitable | **9** |
| ARK avec code `COM` actuel concordant sur le code et département | **615** |
| ARK portant un code présent simultanément sur `COM` et `COMD` | **75** |
| ARK portant un code `COMD` ou `COMA` sans autre type courant | **98** |
| ARK portant un code absent des entrées communales 2026 | **9** |

**Précision :** la catégorie des 615 signifie seulement que **code, région et département concordent avec une commune actuelle**. Elle ne représente ni 615 correspondances lexicales vérifiées, ni 615 identités Pactols–COG nouvellement validées.

Les **775 codes distincts** se répartissent selon les entrées COG 2026 de la façon suivante :

| Types COG 2026 | Codes |
| --- | ---: |
| `COM` seulement | **615** |
| `COMD` seulement | **96** |
| `COM` et `COMD` sous le même code | **54** |
| `COMA` seulement | **1** |
| Code sans entrée en 2026 | **9** |

Les 54 codes `COM/COMD` sont à distinguer des **22 codes partagés entre ARK Pactols** : les deux chiffres ne mesurent pas la même chose.

## Graphes et dédoublonnages

Deux traitements indépendants ont été réalisés sur les données COG officielles :

- `scripts/auditer_lieux_pays_loire_cog.py` : **945 lignes de périodes** et **1 010 lignes de mouvements** rattachées à chacun des ARK concernés ;
- `scripts/construire_graphe_cog_pdl_806.py` : après dédoublonnage des données Insee, **898 périodes code–libellé uniques**, **709 lignes de mouvement uniques** et **1 295 états observés `TYPECOM/COM/LIBELLE`**.

Les états observés incluent les participants à des mouvements qui ne font pas eux-mêmes partie des 775 codes retenus. Une ligne de mouvement peut être associée à plusieurs ARK ; les **709 mouvements distincts ne signifient pas 709 actes juridiques distincts**.

Le graphe JSON inclut la provenance des données, l'association documentaire des transitions aux codes et ARK concernés, ainsi que deux listes vides `alignements_valides_nouveaux` et `geometries_historiques`. Il ne construit **aucune fermeture transitive** ni identité communale supposée à partir du code seul.

## Neuf ARK avec un code historique absent du COG 2026

Les neuf codes ont des périodes ou mouvements dans les fichiers Insee historiques :

| Concept Pactols | Code | Épisode historique principal à conserver |
| --- | --- | --- |
| Saint-Géréon | `44160` | Création d'Ancenis-Saint-Géréon au **2019-01-01** (`MOD 32`) |
| Trèves-Cunault | `49357` | Fusion-association **1974**, puis création Gennes-Val de Loire **2016** |
| Bazouges (Mayenne) | `53024` | Commune associée **1990**, fusion simple **2006** |
| Bernay-en-Champagne | `72033` | Changement de nom **2007** (`MOD 10`) puis commune nouvelle **2019** |
| Saint-Mars-sous-Ballon | `72301` | Commune déléguée **2016**, statut supprimé **2020** |
| La Chapelle-Achard | `85052` | Commune déléguée **2017**, statut supprimé **2024** |
| Château-d'Olonne | `85060` | Les Sables-d'Olonne **2019-01-01**, suppression `COMD` **2019-02-08** |
| Fontaines (Doix lès Fontaines) | `85091` | Commune déléguée **2016**, statut supprimé **2026** |
| Olonne-sur-Mer | `85166` | Les Sables-d'Olonne **2019-01-01**, suppression `COMD` **2019-02-08** |

Les dates et modalités sont fondées sur les champs **avant/après** de `v_mvt_commune_2026.csv` ; elles ne datent pas les contours historiques.

## Neuf ARK sans code communal numérique dans les assertions Pactols

**Six objets supracommunaux :** région Pays de la Loire et départements Loire-Atlantique, Maine-et-Loire, Mayenne, Sarthe et Vendée. Leurs URI `/geo/region/52` et `/geo/departement/*` ne sont pas des codes communaux manquants.

**Trois dossiers spécifiques :**
- **Grandchamp-des-Fontaines** : URI `/geo/commune/493ed29c-e150-4c2e-9880-f94d7002f1f5` (identifiant UUID, non code numérique).
- **Thouarsais-Bouildroux** : URI `/geo/communeDeleguee/ef312e8c-b172-40ed-b169-8bf72e16ba8b` (UUID d'entité déléguée).
- **Cherré-Au** : aucune URI INSEE `exactMatch` communale dans l'export utilisé.

Ne pas transformer ces URI en codes à partir du seul libellé ou de la proximité lexicale : leur instruction doit être individualisée.

## Reproductibilité et publication

Entrées : `docs/lieux/recette/inventaire-pays-de-la-loire.csv` (806 ARK, SHA-256 `ea06d1bddbf53ec49410aa122b9f3e80842f0f770b9f364c3677a0a7c35e91db`) et les fichiers Insee 2026 :

- `v_commune_2026.csv` : `7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3`
- `v_commune_depuis_1943.csv` : `08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee`
- `v_mvt_commune_2026.csv` : `8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1`

Source officielle : https://www.insee.fr/fr/information/8740222

Le fichier `inventaire-pays-de-la-loire.csv` est déposé dans la **branche de recette**, non en production. Les fichiers publics `docs/data/lieux*` et les alignements PACA antérieurement validés restent inchangés.

**Zéro nouvel alignement AdlFI–COG validé, zéro géométrie historique attribuée.**

## Suites d'instruction

1. Contrôler les neuf ARK sans code numérique, dont les trois cas locaux spécifiques, en respectant leur type géographique.
2. Vérifier le degré de concordance des libellés pour les 615 codes `COM` actuels : la concordance du code/département ne suffit pas à une validation éditoriale.
3. Examiner les 709 lignes de mouvements uniques dans une perspective de graphes d'épisodes administratifs, sans assimiler les groupes techniques à des actes officiels.
4. Appliquer le protocole à la **Bourgogne-Franche-Comté (736 ARK dans le corpus actuel)**, avec attention à la couverture XML de la Bourgogne.

Aucune mise en production avant validation éditoriale.
