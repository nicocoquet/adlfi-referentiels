# Martinique — 34 états communaux historiques COG, sans géométries

**16 novembre 2026 · Publication documentaire de la page Lieux.**

## Provenance et méthode

Les **34 épisodes code–libellé** ont été extraits de l'historique COG 2026 de l'Insee, fichier v_commune_depuis_1943.csv, recoupé avec v_mvt_commune_2026.csv dans la [recette du lot 01](../../../recette/lieux/MARTINIQUE-LOT-01-2026.md), PR 51.

- Historique des périodes Insee : SHA-256 **08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee**.
- Mouvements communaux Insee : SHA-256 **8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1**.
- Source de référence : [Code officiel géographique, Insee](https://www.insee.fr/fr/information/2560452).
- Contrôle des données publiques : scripts/verifier_index_public_martinique_2026.py, exécuté sur la CI spécialisée à partir des fichiers COG originaux, avec refus de toute divergence de code, libellé, date ou mouvement.

Les périodes sont enregistrées **avec début inclus et fin exclue** et consultées au **1er janvier de l'année sélectionnée**. Il n'existe dans ces sources **aucune ancienne autorité communale 972 associée à un code disparu distinct des 34 codes actuels**. Cette constatation de source ne garantit pas qu'il n'existe aucune transformation historique antérieure aux premières données COG.

## Chronologie observable

| Année sélectionnée (situation au 1er janvier) | Nombre de codes communaux documentés | Interprétation |
| --- | ---: | --- |
| 1943 et 1946 | 0 | Source sans épisode actif au premier janvier ; ce n'est pas une preuve d'inexistence des communes |
| 1947 | 32 | Première série de périodes ouvertes le 21 mars 1946 |
| 1949 | 32 | Situation avant le 25 mars 1949 |
| 1950 | 33 | Le Morne-Vert (97233), état à partir du 25 mars 1949 |
| 1951 | 34 | Bellefontaine (97234), état à partir du 26 août 1950 |
| 2026 | 34 | Périmètre communal du COG au 1er janvier 2026 |

Les **36 lignes de mouvements** sont groupées sur trois dates : **21 mars 1946 (32 lignes MOD20)**, **25 mars 1949 (deux lignes MOD20)** et **26 août 1950 (deux lignes MOD20)**. Le nombre de lignes COG n'est pas le nombre de communes nouvellement créées ; il peut exister des lignes pour le code conservé et pour le territoire détaché.

Les débuts au **21 mars 1946** sont liés à la première période administrative couverte dans les données COG pour la Martinique. Ils ne doivent pas être interprétés comme la fondation effective des communes martiniquaises à cette date.

## Présentation publique et limites

Les fiches COG 2026 restent consultables comme références contemporaines et conservent leurs ARK Pactols validés **pour le seul millésime 2026**. Un encart COG distinct affiche, à la date du curseur, le code et le nom **documentés par l'Insee**.

Pour les années où aucun épisode n'est actif, le navigateur affiche **« Aucun épisode actif n'est attesté »**, sans en inférer l'inexistence du lieu. Les premières dates d'attestation sont affichées en contexte.

L'interface ne propose aucun quatrième niveau administratif : le sélecteur reste **Région / Département / Commune**.

**Aucun polygone historique de Martinique n'est publié, aucune géométrie 2026 n'est rétroprojetée aux périodes précédentes, aucun lien historique Pactols–COG n'est inféré et aucune succession juridique n'est fabriquée.** Les contours 2026 validés sur le plan topologique demeurent des candidats à l'instruction cartographique, pas une preuve de représentation des périodes antérieures.
