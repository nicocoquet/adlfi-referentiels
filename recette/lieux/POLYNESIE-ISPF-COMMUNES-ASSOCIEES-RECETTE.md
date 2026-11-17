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

Cette PR commence comme **audit documentaire**, sans modification de `docs/data/`, ni des 176 relations Pactols communales ou des 4 relations Pactols de collectivités.
