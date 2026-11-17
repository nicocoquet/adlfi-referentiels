# Polynésie française — préinstruction de la nomenclature ISPF

**17 novembre 2026 — recette documentaire préalable à toute création d'autorité infracommunale.**

## Source première

L'[Institut de la statistique de la Polynésie française (ISPF)](https://www.ispf.pf/ispf/referentiels) publie une nomenclature géographique officielle : [Télécharger les codes géographiques (XLSX)](https://www.ispf.pf/content/uploads/Codes_geographiques_ce46ed21ee.xlsx).

La source distingue les deux arbres qui **ne sont pas substituables** :

- **Administratif** : 5 subdivisions → 48 communes principales → 98 communes associées dans 30 communes ; les 18 communes restantes sont non subdivisées en communes associées ;
- **Géographique** : subdivision → île. Le découpage `CODGEO` de l'ISPF associe **un code d'unité administrative fine sur 3 positions** et **un code d'île rattachée sur 2 positions**.

Il existe **116 unités de la nomenclature fine** (98 communes associées effectives + 18 communes sans association, codifiées conventionnellement par le code communal ISPF sur deux positions suivi de `0`). **Il ne faut donc pas enregistrer 116 communes associées.**

Les 48 identifiants communaux `98711`–`98758` du COG INSEE et les 4 ARK des collectivités validés dans les PR précédentes restent conservés.

## Qualité et homonymies

L'ISPF cite explicitement l'homonymie **Avera** (code ISPF `501` de Taputapuatea ; code `441` de Rurutu), ainsi que les îles rattachées et les communes étendues à plusieurs îles. Le seul nom ne constitue donc pas une clé d'autorité. Une éventuelle correspondance Pactols doit attendre une instruction explicitement sourcée, sans transfert d'ARK d'une commune à ses unités fines.

## Méthode de ce lot

1. Télécharger le classeur officiel ISPF dans GitHub Actions et enregistrer son SHA-256 ;
2. inventer un **minimum de structure** : inspecter ses feuilles et les colonnes **réelles** avant de choisir un parseur durable ;
3. recouper les codes des 48 communes principales avec l'index COG du site ;
4. classer exactement **98 autorités associées réelles** et 18 unités conventionnelles sans association ;
5. qualifier les 30 rattachements, Avera et les codes ISPF susceptibles d'être lexicalement ambigus ;
6. ne publier aucun code, aucune géométrie ni aucune date historique nouvelle tant que le rapport reproductible n'est pas concluant.

## Résultat de l'audit effectif des cinq feuilles ISPF

La [CI de recette n°44078841706](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44078841706) a téléchargé le **classeur officiel `Codes_geographiques_ce46ed21ee.xlsx` (52 132 octets, SHA-256 `d84f9a69f2c64f744ee0719b01c4841953019d45a1fb29b8abb0db2f3f0176e6`)**, puis recoupé exhaustivement les identifiants avec les 48 communes COG 2026.

| Nomenclature ISPF réelle | Éléments |
| --- | ---: |
| Communes principales dans l'onglet `Commune` | **48** |
| Vraies communes associées dans `Commune associée` | **98** |
| Unités conventionnelles pour communes sans association, code finissant par `0` | **18** |
| Communes principales comportant des associées | **30** |
| Subdivisions administratives | **5** |
| Codes d'îles dans l'onglet `Ile` | **119** |
| `CODGEO` dans l'onglet `Geo` | **179** |

Les 48 correspondances entre `IDCom` (deux positions ISPF) et `987XX` (COG INSEE) sont validées par **code et subdivision**, non par simple égalité des noms. Une variante de libellé est explicitement conservée : **`Faa'a` (ISPF) / `Faaa` (COG `98715`)**.

Les 98 unités associées ont toutes un identifiant `IDComas` à trois positions, dont les deux premières correspondent à leur `IDCom`. Les 18 codes conventionnels finissent par `0` et ne sont **pas** des communes associées supplémentaires.

### Deux exceptions géographiques confirmées

L'onglet `Geo` contient **deux `CODGEO` dont le préfixe ne correspond pas au `IDComas` de la même ligne** :

- `43001` : îles Maria, partie **Rimatara**, `IDComas=431` (**Amaru**), `IDIle=45` ;
- `44001` : îles Maria, partie **Rurutu**, `IDComas=441` (**Avera (Rurutu)**), `IDIle=45`.

Ces deux cas sont isolés et explicitement couverts par une règle de recette. Leur origine devra être documentée plus précisément avant tout lien de géométrie ou toute reconstruction automatique du CODGEO. Il serait méthodologiquement faux de « corriger » leurs identifiants de façon arithmétique.

### Deux Avera distinctes

- **`441` Avera (Rurutu)** → `98744` Rurutu ;
- **`501` Avera (Taputapuatea)** → `98750` Taputapuatea.

Les libellés officiels ISPF sont déjà contextualisés : ils seront conservés tels quels, sans fusion d'autorités.

La nomenclature ISPF comporte **119 codes d'îles** dans le fichier téléchargé, tandis que la page d'explication ISPF décrit **121 îles** ; les périmètres de comptage ne doivent pas être présumés équivalents. Ce différentiel ne concerne pas les 98 communes associées, mais appelle un contrôle spécifique avant le chantier géométrique.

**Cette PR est une recette documentaire** : zéro nouvel alignement, zéro contour historique, zéro nouvelle autorité publiée. Le rapport JSON complet du classeur est archivé dans les artefacts GitHub Actions, indépendamment des données exposées sur le site.
