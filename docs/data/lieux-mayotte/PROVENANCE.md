# Mayotte — 34 épisodes COG, transition documentaire COMER–DROM

**17 novembre 2026 — publication documentaire sans géométries historiques ni nouvel alignement Pactols.**

## Deux familles COG pour les mêmes 17 communes

Les **17 codes communaux** `97601` à `97617` possèdent, dans les tables historiques du **Code officiel géographique 2026**, deux épisodes chacun, dont les périodes sont raccordées à la date du **31 mars 2011** :

| Source officielle | Début inclus | Fin exclusive | Nature documentaire |
| --- | --- | --- | --- |
| `v_commune_outremer_depuis_1943.csv` | 23 février 2007 | 31 mars 2011 | Commune de territoire d'outre-mer — famille COMER |
| `v_commune_depuis_1943.csv` | 31 mars 2011 | État actuel (COG 2026) | Commune d'un DROM |

Les deux épisodes sont reliés **par le même code et le même libellé**. Le **31 mars 2011 marque ici un changement de statut administratif et de famille des tables COG**, et ne constitue **pas** une date de création des 17 communes. De même, le 23 février 2007 est la première date de la série historique étudiée, non une preuve d'apparition de ces communes.

Les **34 épisodes datés** sont publiés dans `chronologie-cog-2026.json`. Le curseur de l'interface montre **l'état au 1er janvier** de chaque année :

| Année sélectionnée | Épisodes actifs | Famille COG |
| --- | ---: | --- |
| 2007 | 0 — pas encore d'épisodes dans le jeu exploité au 1er janvier | Non attestée |
| 2008 | 17 | COMER |
| 2011 | 17 | COMER (avant le changement du 31 mars) |
| 2012 | 17 | DROM |
| 2026 | 17 | DROM |

Ces observations ne prouvent **ni l'absence des lieux antérieurement ni l'identité géométrique intemporelle de chacun des codes**.

## Distinction avec la collectivité de Mayotte

L’[INSEE](https://www.insee.fr/fr/information/7929497) établit que le Département de Mayotte est devenu une collectivité à statut particulier le **31 mars 2011**, initialement codée **`976D`**, et que le **Département-Région de Mayotte** reçoit le code institutionnel **`976R` au 1er janvier 2026**. Ce code **ne remplace aucun** des codes des **17 communes** dans le référentiel.

Le présent module ne crée pas d'entité géométrique historique ou d'ARK Pactols pour `976D` / `976R`. L'échelon territorial public reste **Région / Département / Commune**.

## Liens Pactols : décisions indépendantes du COG historique

- **16 correspondances Pactols–COG validées pour le seul millésime 2026** demeurent inchangées.
- **Dembeni (97607)** : la forme de l'ARK `26678/crtZcuFSJVYZU` a été confirmée par l'éditeur, mais **la correspondance au code communal n'a pas été approuvée**. Elle reste identifiée, non alignée ; il ne faut pas la remplacer par un identifiant commençant par `pcrt`.
- Les 34 périodes historiques **n'entraînent aucune validation Pactols supplémentaire** ni rétroprojection des 16 liens du millésime 2026.

## Provenance, validation et limites

Les trois CSV COG Insee originaux sont vérifiés **octet par octet** par les empreintes SHA-256 suivantes :

| Fichier officiel | SHA-256 |
| --- | --- |
| `v_commune_outremer_depuis_1943.csv` | `d2e2d3b376540d5c5e624e1cdf3d6a1959f6f24d6763268eec67883fe82ce748` |
| `v_commune_depuis_1943.csv` | `08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee` |
| `v_commune_2026.csv` | `7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3` |

Le script `scripts/verifier_index_public_mayotte_2026.py` confronte les **34 lignes publiques** aux trois tables officielles et refuse les divergences de codes, noms, dates, famille et décisions éditoriales. Le moteur JavaScript impose la même séparation ; des tests Playwright inspectent la frise et la fiche Dembeni.

Sources : [INSEE — COG 2026](https://www.insee.fr/fr/information/8740222) ; [INSEE — Collectivités territoriales à statut particulier](https://www.insee.fr/fr/information/7929497) ; [INSEE — documentation des communes depuis 1943](https://www.insee.fr/fr/information/2560452). Réexamen des décisions éditoriales du [dossier n°30](https://github.com/nicocoquet/adlfi-referentiels/pull/30), qui reste en brouillon.

**Aucun contour historique qualifié, aucune relation de succession inférée, aucune nouvelle correspondance Pactols.**
