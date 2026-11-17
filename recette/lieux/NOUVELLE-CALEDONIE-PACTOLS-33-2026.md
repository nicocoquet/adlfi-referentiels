# Nouvelle-Calédonie — audit Pactols–COG des 33 communes 2026

**17 novembre 2026 — instruction RDF de référence, sans publication d'ARK.**

## Périmètre

Le socle [COG Nouvelle-Calédonie](NOUVELLE-CALEDONIE-COG-HISTORIQUE-2026-RECETTE.md) publié contient **33 communes** de code `988xx` au millésime `2026-01-01`, sans alignement Pactols communal encore validé. Les trois provinces, les huit aires coutumières et l'autorité territoriale 988 sont des catégories distinctes. **Poya (98827)** relève de deux provinces ; **Kouaoua (98833)** possède un épisode communal COG ouvert le 25 avril 1995 (division de Canala). Ces observations historiques ne valident aucun lien Pactols.

## Sources et traitement

- **RDF Pactols Lieux** : dépôt `frantiq/PACTOLS`, commit `69bf9697e24cefd645a69465bbd271702786285a`, fichier `Pactols_Lieux_th17_20260722.rdf`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.
- **COG INSEE 2026** : six tables originales à SHA-256 vérifiés selon `scripts/auditer_cog_polynesie_2026.py`. L'audit historique de Nouvelle-Calédonie valide leurs 33 codes et libellés contre l'index COG publié.

Le script `scripts/auditer_pactols_nouvelle_caledonie_2026.py` récupère les `skos:exactMatch` typés `http(s)://id.insee.fr/geo/commune/988xx`, ARK source, libellé français, variantes, dépréciations, remplacements et autres URI INSEE éventuellement portées par le même concept. Il réutilise le parseur RDF en flux déjà testé pour la Polynésie.

**Seules** les assertions `skos:exactMatch` explicites, uniques et non dépréciées, associées à un concept dont le libellé correspond à la commune administrative, sont classées `ELIGIBLE_SELON_REGLE`. Les autres états sont `A_INSTRUIRE_MULTIPLICITE`, `A_INSTRUIRE_ONTOLOGIE_OU_DIVERGENCE` ou `SANS_ASSERTION_EXPLICITE`. Un homonyme lexical reste diagnostique et ne crée jamais d'identifiant validé.

## Points d'attention éditoriaux

- Les libellés « île », « îlot », « archipel », « atoll », « district » et « royaume » déclenchent un contrôle de catégorie même en présence d'une assertion INSEE explicite.
- Les tribus et aires coutumières néo-calédoniennes ne deviennent pas des communes par homonymie ; les subdivisions et les provinces ne sont pas associées automatiquement aux ARK des communes.
- Un concept exactMatch vers plusieurs codes, une famille d'URI autre que `geo/commune`, une dépréciation, ou un désaccord de libellé reste **à instruire**.
- Ne pas transférer l'autorité de Canala à Kouaoua : l'épisode COG de 1995 est une preuve d'évolution administrative, pas de synonymie d'identifiant.
- Les dates de première attestation dans le COG n'établissent pas nécessairement les dates historiques de création des collectivités.

## Livraison et décision

La CI `lieux-nouvelle-caledonie-pactols-2026.yml` contrôle les sources par SHA-256, exécute deux fois la qualification des 33 codes et archive le rapport JSON sous les artefacts de recette. Les nombres d'assertions réellement trouvées et les ARK seront consignés **après le premier calcul effectif** : aucune cardinalité Pactols n'est supposée.

**Aucune publication d'ARK, de lien, de toponyme ou de géométrie dans cette PR.** Toute décision de validation fera l'objet d'un registre éditorial et d'une recette de publication séparée.
