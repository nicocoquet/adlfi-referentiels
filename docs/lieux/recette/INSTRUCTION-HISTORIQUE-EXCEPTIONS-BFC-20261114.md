# Bourgogne-Franche-Comté — instruction historique de 25 codes anciens et quatre ARK particuliers

**14 novembre 2026 — PR n°24 — recette non validante.** Cette note complète `BILAN-BOURGOGNE-FRANCHE-COMTE-736-COG2026-20261114.md`. La faible représentation de la Bourgogne tient à l'avancement éditorial de la mise au format XML des notices, **pas à un défaut démontré de l'extracteur**.

## 1. Sources, méthode et contrôle

- **Pactols** : `codes-historiques-absents-bfc-25.csv` (25 ARK, code numérique déclaré dans l'export SKOS mais absent des entrées communales COG 2026) et `codes-partages-ark-bfc-2.csv` (4 ARK pour 2 codes).
- **Insee** : `v_commune_2026.csv`, `v_commune_depuis_1943.csv`, `v_mvt_commune_2026.csv`, provenant du [COG 2026 officiel](https://www.insee.fr/fr/information/8740222), fichiers vérifiés par SHA-256.
- **Reproductibilité** : `scripts/instruire_exceptions_bfc_cog.py` et `tests/test_instruire_exceptions_bfc_cog.py`, exécutés avec succès dans [GitHub Actions](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43628518269).
- **Niveau de preuve** : les couples `TYPECOM_AV/COM_AV/LIBELLE_AV` et `TYPECOM_AP/COM_AP/LIBELLE_AP` sont conservés avec les dates et modalités officielles. Les destinations sont des **communes réceptrices immédiates**, non des équivalences entre concepts Pactols.

Le contrôle porte sur **25 codes historiques, 42 lignes de mouvements, 2 codes portés chacun par deux ARK, et 2 communes associées interdépartementales**. Il ne valide aucun nouvel alignement AdlFI et n'attribue aucune géométrie historique.

## 2. Les 25 anciennes identités communales : cinq profils

### A. Quatre fusions simples (`MOD=31`)

| Ancienne entité et code | Date | Réception administrative immédiate |
| --- | --- | --- |
| Arcier `25023` | 1974-04-01 | Vaire-Arcier `25575` ; dénomination actuelle du code : **Vaire** |
| Champvans-les-Baume `25118` | 1973-01-01 | Baume-les-Dames `25047` |
| Droitfontaine `25206` | 1973-01-01 | Belleherbe `25051` |
| Sézéria `39515` | 1973-01-01 | Orgelet `39397` |

### B. Douze rattachements par création ou modification de commune nouvelle (`MOD=32`)

| Ancienne entité et code | Date | Commune réceptrice après le mouvement |
| --- | --- | --- |
| Arguel `25027` | 2019-01-01 | Fontain `25245` |
| Chaudefontaine `25137` | 2018-01-01 | Marchaux-Chaudefontaine `25368` |
| Châtillon-sur-Lison `25134` | 2022-01-01 | Cussey-sur-Lison `25185` |
| Sancey-le-Long `25530` | 2016-01-01 | Sancey `25529` |
| Chatonnay `39123` | 2017-01-01 | Valzin en Petite Montagne `39290` |
| Chisséria `39148` | 2018-01-01 | Arinthod `39016` |
| Cézia `39089` | 2019-01-01 | Saint-Hymetière-sur-Valouse `39137` |
| Fétigny `39224` | 2017-01-01 | Valzin en Petite Montagne `39290` |
| Lavans-sur-Valouse `39287` | 2019-01-01 | Saint-Hymetière-sur-Valouse `39137` |
| Saint-Hymetière `39483` | 2019-01-01 | Saint-Hymetière-sur-Valouse `39137` |
| Savigna `39506` | 2017-01-01 | Valzin en Petite Montagne `39290` |
| Ciel `71131` | 2025-01-01 | Verdun-Ciel `71566` |

Il ne faut pas déduire de la seule modalité `32` que chaque commune réceptrice aurait été créée *ex nihilo* à cette date. Certains événements modifient des communes nouvelles ou intègrent un territoire à une commune existante. Les états avant/après demeurent la preuve utile.

### C. Sept créations de communes nouvelles suivies de la suppression du statut délégué (`MOD=32`, puis `35`)

| Ancienne entité | Commune réceptrice | Création/association | Suppression du statut COMD |
| --- | --- | --- | --- |
| Vauchamps `25587` | Bouclans `25078` | 2018-01-01 | **2021-03-15** |
| Coisia `39158` | Thoirette-Coisia `39530` | 2017-01-01 | **2020-01-01** |
| Essia `39215` | La Chailleuse `39021` | 2016-01-01 | **2020-03-15** |
| Mirebel `39332` | Hauteroche `39177` | 2016-01-01 | **2020-03-15** |
| Saint-Laurent-la-Roche `39488` | La Chailleuse `39021` | 2016-01-01 | **2020-03-15** |
| Varessia `39544` | La Chailleuse `39021` | 2016-01-01 | **2020-03-15** |
| Villechantria `39564` | Val Suran `39485` | 2017-01-01 | **2020-03-15** |

La suppression du statut `COMD` **n'efface ni l'ancien lieu ni son ARK Pactols**. Un ancien contour ne peut pas être remplacé par celui de la commune parente au millésime 2026.

### D. Une fusion-association transformée en fusion simple (`MOD=33`, puis `34`)

**Gonvillars (`70270`)** : `COM → COMA` au **1972-12-31** dans l'ensemble Saulnot (`70477`), puis `COMA → COM 70477 Saulnot` au **1997-05-01**. Conserver les deux épisodes et la distinction entre les deux modalités de fusion.

### E. Un changement de nom suivi d'une création de commune nouvelle (`MOD=10`, puis `32`)

**Vaux-les-Prés (`25593`)** : `Vaux → Vaux-les-Prés` au **1961-12-28**, sans changement de code, puis intégration à **Chemaudin et Vaux (`25147`)** au **2017-01-01**. L'événement de 1961 ne doit pas être décrit comme une création de commune nouvelle.

## 3. Deux codes conservés à travers deux autorités Pactols

| Code partagé | Concepts Pactols (ARK distincts) | Épisode Insee |
| --- | --- | --- |
| `25368` | Marchaux `26678/pcrtHVMF65Ey3z` et Marchaux-Chaudefontaine `26678/pcrtPEJhK71UsV` | **2018-01-01** : Marchaux et Chaudefontaine `25137` aboutissent à Marchaux-Chaudefontaine `25368` |
| `25529` | Sancey-le-Grand `26678/pcrtSYhbegbvSU` et Sancey `26678/pcrtqvgozFu6dO` | **2016-01-01** : Sancey-le-Grand et Sancey-le-Long `25530` aboutissent à Sancey `25529` |

**Arbitrage recommandé :** conserver les quatre ARK, enregistrer les épisodes administratifs correspondants et leur source COG. Un code partagé ne signifie ni doublon Pactols ni identité territoriale inchangée.

## 4. Deux communes associées historiques hors de leur ancien département

| ARK documenté | Code historique | Événement `MOD=33` | Statut au COG 2026 |
| --- | --- | --- | --- |
| **Antorpe** | `39012` (Jura) | **1974-06-01** : `COM → COMA` et rattachement à Saint-Vit | `COMA 39012` ; `COMPARENT=25527`, **Saint-Vit**, Doubs |
| **Frettes** | `52210` (Haute-Marne) | **1974-07-01** : `COM → COMA` et rattachement à Champlitte | `COMA 52210` ; `COMPARENT=70122`, **Champlitte**, Haute-Saône |

Ce sont **deux codes historiques authentiques**, pas deux fautes de préfixe départemental. La hiérarchie Pactols actuelle et le code de l'ancienne commune ont des référentiels temporels différents : les deux informations doivent coexister.

## 5. Sorties et arbitrages en attente

L'artefact GitHub Actions `audit-lieux-bfc-736-cog2026` comporte le sous-répertoire `instruction-exceptions/` :

- `instruction-25-codes-historiques.csv` : 25 dossiers, épisodes de noms, modalités, dates et réceptions administratives immédiates ;
- `preuves-mouvements-25.csv` : **42 lignes originales de mouvements**, avec tous leurs champs avant/après ;
- `deux-codes-partages-ark.csv` : deux couples d'ARK et opérations correspondantes ;
- `antorpe-frettes.csv` : code historique, date d'association, `COMPARENT` et commune parente au COG 2026 ;
- `rapport-instruction-bfc.json` : cardinalités, contrôles SHA-256, catégories et limites.

Les arbitrages éditoriaux sont volontairement laissés ouverts sur **l'identité des concepts Pactols par rapport aux épisodes communaux**, la portée temporelle des toponymes et l'éventuelle sélection de géométries historiques adaptées. Les sources Insee établissent les mouvements administratifs ; elles ne suffisent pas à valider des alignements éditoriaux ni à reconstruire les contours de tous les états passés.

**Aucune modification du référentiel public et aucune fusion d'ARK. PR n°24 maintenue en brouillon.**
