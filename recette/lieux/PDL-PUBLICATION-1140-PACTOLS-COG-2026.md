# Pays de la Loire — publication de 1 140 correspondances Pactols–COG 2026

**17 novembre 2026. Index documentaire distinct des épisodes historiques COG.**

## Fondement et sources

L'audit régional PR 97 et le registre de recette PR 104 ont examiné les **1 228 communes COG 2026 de la région Pays de la Loire** (REG=52) face au RDF Pactols Lieux épinglé.

- **1 140 couples** `skos:exactMatch` univoques éligibles et contrôlés, dans les départements 44, 49, 53, 72 et 85.
- **88 exceptions non publiées** : 60 communes avec plusieurs ARK, 24 divergences de libellé/statut/URI et quatre communes sans URI de code reconnue : Grandchamp-des-Fontaines (44066), L’Oie (85165), Sainte-Florence (85212), Rives-du-Fougerais (85292).
- Toutes les URI INSEE supplémentaires ont été vérifiées dans le RDF brut pour les 1 140 concepts retenus ; aucune contradiction n’a été trouvée.
- Source Pactols : `Pactols_Lieux_th17_20260722.rdf`, commit `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.
- Source COG : `v_commune_2026.csv` SHA-256 `7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3`.
- CSV des décisions reproductible, SHA-256 `81c49e32e5a443a1dd2e9f40e2d82c842a72ab1f82d81833fd51f02ae9d71335`.

## Fichiers de publication

- `recette/lieux/PDL-VALIDATIONS-PACTOLS-COG-2026.csv` : registre de 1 140 décisions par règle, porté au 1er janvier 2026.
- `docs/data/lieux-chronologie/pactols-pdl-2026.json` : index public documentaire `adlfi.lieux.pactols.pdl.2026.public.v1`.
- `docs/assets/lieux-pdl-pactols.js` : vérification du millésime, des 1 140 couples, de l’unicité des ARK, des codes COG, de la provenance et des 88 exclusions.
- `docs/assets/lieux-multiechelon.js` : recherche par libellé, code et ARK, puis fiche communale avec correspondance Pactols **validée pour 2026 seulement**.

Le COG historique `cog-pdl.json`, les mouvements, les anciens périmètres, les rapports d’homonymies et les contours 2026 restent inchangés. Les collisions de codes historiques ne justifient **aucune succession de concepts Pactols** et les 88 dossiers non univoques ne reçoivent aucune identification automatiquement.

## Contrôle avant fusion

Le workflow spécialisé reconstitue deux exemplaires identiques octet à octet des CSV et JSON, compare le SHA du registre à la PR 104, publie un artefact vérifiable, puis contrôle Python, Node et Chromium (fiche, recherche ARK, frise 1975, cas 44066). Il teste également la Corse et la BFC, et ne versionne les fichiers générés que dans la branche de PR **après réussite de la recette**.

Aucune géométrie historique n'est homologuée par cette publication. Le chantier séparé des contours communaux ultramarins 2026 est suivi dans l'[issue 105](https://github.com/nicocoquet/adlfi-referentiels/issues/105).
