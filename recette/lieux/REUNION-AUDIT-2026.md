# La Réunion — contrôle des 24 candidats Pactols–COG 2026

**17 novembre 2026 — recette documentaire, sans publication.**

Ce lot reprend les 24 candidats déjà instruits dans la PR #30 (`recette/lieux/REVUE-REUNION-24-COG2026-20261115.csv`) sous une copie traçable de 24 lignes. La règle d'alignement est celle de `recette/lieux/POLITIQUE-ALIGNEMENT-PACTOLS-COG.md` : URI INSEE citée sous `skos:exactMatch`, univocité, concept non déprécié et non remplacé, libellé compatible, référence COG au 1er janvier 2026.

## Preuves à contrôler en CI

- COG INSEE : `v_commune_2026.csv`, `v_commune_depuis_1943.csv`, `v_mvt_commune_2026.csv`, empreintes SHA-256 figées par `scripts/recuperer_cog_2026.py`.
- Pactols : RDF Lieux `th17` du 22 juillet 2026, commit Frantiq `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.
- 24 codes courants `97401`–`97424` ; 24 candidats ARK distincts ; examen des éventuels autres `exactMatch` attachés à chaque concept.
- **Le Port (97407)** : concept `26678/pcrtIKvRT9vwUl` confirmé explicitement par l'éditeur ; les homonymes métropolitains ne sont pas retenus.
- **Saint-Louis (97414) / Cilaos (97424)** : une division au **5 février 1965**, deux lignes COG `MOD=20`. Le code 97414 subsiste, sans maintien garanti de la même emprise. Les 23 entrées du 21 mars 1946 ne démontrent pas des créations légales.

## Sortie et invariants

Le script `scripts/auditer_reunion_2026.py` qualifie chaque candidat comme `ELIGIBLE_SELON_REGLE` ou `A_INSTRUIRE`, en conservant toutes les preuves dans un rapport JSON de CI. Deux générations sont comparées octet par octet. Tant que la conformité des 24 candidats n'est pas démontrée, **aucun alignement n'est publié**.

La PR n'ajoute aucun `skos:exactMatch`, aucune géométrie, aucune relation de succession et ne modifie **aucun fichier du site `docs/`**. La validation éventuelle de ces liens portera uniquement sur l'état COG 2026. Les limites historiques des communes restent à qualifier séparément.

## Résultats

À compléter **à partir des résultats effectivement constatés en CI**, sans présumer que les 24 candidats sont éligibles.
