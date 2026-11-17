# La Réunion — historique communal COG (1943–2026)

**17 novembre 2026 — publication documentaire uniquement.** Les états communaux sont distingués des géométries et des relations Pactols 2026.

## Sources et méthode

Les **24 périodes code–libellé COG** documentées dans `v_commune_depuis_1943.csv` sont confrontées aux **25 lignes de mouvements** de `v_mvt_commune_2026.csv` de l'Insee. Les empreintes SHA-256 sont :

- `v_commune_2026.csv` : `7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3`
- `v_commune_depuis_1943.csv` : `08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee`
- `v_mvt_commune_2026.csv` : `8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1`

La source Pactols, revue dans la [PR n°57](https://github.com/nicocoquet/adlfi-referentiels/pull/57), puis approuvée pour le seul millésime 2026 dans la [PR n°58](https://github.com/nicocoquet/adlfi-referentiels/pull/58), fournit **24 correspondances ARK–COG actuelles**. Elles ne sont pas rétroactives.

Le moteur présente les états **au 1er janvier** de l'année sélectionnée. Les bornes des périodes sont **début inclus et fin exclusive**, sans interpolation de formes géographiques.

## Chronologie au 1er janvier

| Année | Communes dont un épisode est actif dans l'historique exploité |
| --- | ---: |
| 1943 / 1946 | 0 |
| 1947 | 23 |
| 1965 | 23 |
| 1966 | 24 |
| 2026 | 24 |

Les **23 observations initiales commencent le 21 mars 1946**. Il ne faut pas interpréter ce point de départ des données comme la création légale des 23 communes ; un nombre nul au **1er janvier 1946** ne signifie pas que les communes n'existaient pas.

## Saint-Louis (97414) et Cilaos (97424) : événement du 5 février 1965

Le fichier des mouvements contient **deux lignes `MOD=20` décrivant une seule division** :

| Avant | Après | Interprétation |
| --- | --- | --- |
| 97414 Saint-Louis | 97414 Saint-Louis | Code et libellé conservés, emprise réduite |
| 97414 Saint-Louis | 97424 Cilaos | Nouveau code et nouvelle commune |

Il existe **une seule période code–libellé pour Saint-Louis dans la source**, ouverte au 21 mars 1946 ; il serait faux de fabriquer deux épisodes COG code–libellé en raison du seul changement de périmètre. En revanche, les fiches indiquent que Saint-Louis a une configuration territoriale **antérieure** à la division pour les états au 1er janvier jusqu'en 1965, puis **postérieure** à partir du 1er janvier 1966. Cilaos n'est présente que dans les états au 1er janvier 1966 et suivants, son épisode démarrant au **5 février 1965**.

La date de l'événement est attestée mais les **contours respectifs avant/après 1965 ne sont pas disponibles dans cette publication**. Aucune géométrie 2026 n'est rétroprojetée ou légendée comme une limite ancienne.

## Garanties

- Aucun ARK Pactols nouveau : les 24 correspondances approuvées pour **2026** sont inchangées.
- Aucun polygone historique, successeur inféré, nouvelle identité juridique permanente ou changement de type territorial.
- Le code courant **97414** est conservé sans supposer une emprise identique à travers la division.
- L'interface reste **Région / Département / Commune** ; ces états sont des attributs documentaires des fiches communales.
- Les données publiques sont revérifiées contre les fichiers d'origine par `scripts/verifier_index_public_reunion_2026.py` et la CI.

Sources : [Insee — Code officiel géographique](https://www.insee.fr/fr/information/2560452) ; [Insee — Saint-Louis](https://www.insee.fr/fr/metadonnees/geographie/commune/97414-saint-louis) ; [Insee — Cilaos](https://www.insee.fr/fr/metadonnees/geographie/commune/97424-cilaos).
