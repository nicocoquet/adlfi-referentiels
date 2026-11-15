# Lieux AdlFI — premier audit COG des cinq DROM

**15 novembre 2026 — préinstruction documentaire non validante.** Le module chronologique de quatre régions a été publié dans la PR #29 ; la présente note ouvre le chantier distinct de la géographie ultramarine.

## Source effectivement examinée

Trois fichiers officiels Insee, COG 2026 : `v_commune_2026.csv`, `v_commune_depuis_1943.csv`, `v_mvt_commune_2026.csv`. Les empreintes SHA-256 sont respectivement :

- `7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3`
- `08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee`
- `8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1`

Source : https://www.insee.fr/fr/information/8740222

Les codes INSEE sont conservés comme chaînes, et les lignes `COM` seules sont comptées pour les périodes historiques.

## Résultats observés dans les trois CSV

| Territoire | Code DEP | COM 2026 | Codes COM historiques | Périodes COM | Lignes de mouvements touchant les codes |
| --- | --- | ---: | ---: | ---: | ---: |
| Guadeloupe | 971 | 32 | 34 | 35 | 37 |
| Martinique | 972 | 34 | 34 | 34 | 36 |
| Guyane | 973 | 22 | 26 | 41 | 52 |
| La Réunion | 974 | 24 | 24 | 24 | 25 |
| Mayotte | 976 | 17 | 17 | 17 | 17 |
| **Total** | | **129** | **135** | **151** | **167** |

Les 167 lignes sont des **lignes de mouvement COG**, pas 167 actes ou événements indépendants. Les historiques observés dans ces fichiers débutent le **21 mars 1946** pour Guadeloupe, Martinique, Guyane et La Réunion, et le **31 mars 2011** pour Mayotte ; ces bornes ne doivent pas être étendues par hypothèse.

## Trois dossiers historiques prioritaires

1. **Saint-Barthélemy (97123) et Saint-Martin (97127)** : événements `MOD=30` datés du **23 février 2007**, avec disparition de l'état `COM` ; poursuivre l'instruction dans les tables de collectivités d'outre-mer (COMER), sans conclure à une disparition du lieu ou à une identité Pactols.
2. **Guyane** : mouvements du **27 mars 1969** comportant des fusions `MOD=31` et changements de dénomination `MOD=10`; codes historiques `97351`, `97354`, `97355`, `97359` à examiner. Ne pas rétroprojeter un contour actuel.
3. **Mayotte** : 17 communes `COM` au COG 2026 ; la collectivité à compétences départementales est `976R` depuis le 1er janvier 2026, code de niveau institutionnel différent des codes de communes (source Insee : https://www.insee.fr/fr/information/7929497).

## Second volet à instruire

Le COG 2026 comporte des fichiers **spécifiques** aux collectivités et territoires français d'outre-mer : `v_comer_2026.csv`, `v_tom_depuis_1943.csv`, `v_commune_comer_2026.csv`, `v_commune_outremer_depuis_1943.csv`. Ils sont identifiés dans le catalogue officiel mais **n'ont pas encore été dépouillés dans cette note**.

Leur usage nécessite de respecter `NATURE_ZONAGE` (communes, circonscriptions, districts, autres zonages), notamment pour les cinq districts des **TAAF**. L'historique de ces données peut également couvrir des territoires anciennement français : ne pas traiter toutes les lignes historiques comme des territoires actuels.

La future cartographie mondiale devra fournir un sélecteur par bassin ou territoire, un chargement des géométries à la demande, des identités administratives typées et une distinction stricte entre contours millésimés et états historiques.

## Statut

**0 nouvel alignement Pactols–COG validé, 0 géométrie historique attribuée, aucune donnée outre-mer publiée dans la carte.** La PR de recette doit rester en brouillon jusqu'à l'acquisition et au contrôle des tables COMER et des contours adaptés.

Le paquet de contrôle complet (129 COM, 151 périodes, 167 lignes, synthèse et manifeste) a été généré séparément dans la conversation du 15 novembre 2026.
