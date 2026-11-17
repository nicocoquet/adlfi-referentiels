# Décision éditoriale — Saint-Pierre (97502) ↔ Pactols

**17 novembre 2026.** La validation est expressément confirmée par l'éditeur AdlFI pour le code communal **`97502`**, ARK **`26678/pcrtYQmFfwxLq8`**.

## Éléments de preuve

Le RDF Pactols-Lieux Frantiq (`Pactols_Lieux_th17_20260722.rdf`, commit `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`) porte un **`skos:exactMatch`** vers **`http://id.insee.fr/geo/commune/97502`**. Le concept est non déprécié et non remplacé, et ne présente pas de code INSEE concurrent dans l'audit [Saint-Pierre-et-Miquelon](SAINT-PIERRE-MIQUELON-PACTOLS-2026-RECETTE.md).

Son `prefLabel` français est **« île Saint-Pierre (Saint-Pierre-et-Miquelon) »**, alors que le libellé COG du code `97502` est **« Saint-Pierre »** (commune administrative). Cette divergence **subsiste dans le RDF de référence**. La décision ci-dessus est **une exception nominative explicitement arbitrée par l'éditeur**, pas une nouvelle règle d'équivalence entre îles et communes.

L'éditeur prévoit de solliciter Pactols pour corriger le libellé. **La correction n'a pas encore été constatée** ; il ne faut ni la simuler, ni remplacer la valeur sourcée dans les preuves du référentiel.

## Portée et publication

La décision `VALIDE_ADLFI_2026` porte **uniquement sur le couple ARK Pactols / commune INSEE 97502 au 1er janvier 2026**. Elle n'affirme ni identité exacte des géométries insulaire et communale ni validation historique rétroactive. Le concept `97501` Miquelon-Langlade reste **éligible sans nouvelle décision éditoriale dans cette tranche**.

Le CSV [SAINT-PIERRE-97502-DECISION-PACTOLS-COG-2026.csv](SAINT-PIERRE-97502-DECISION-PACTOLS-COG-2026.csv) enregistre la décision, l'assertion explicite, le libellé source divergent et l'attente d'une **recette distincte pour la publication**. Le total de l'index public demeure **176 correspondances communales** jusqu'à son déploiement. Ne pas présenter la décision documentaire comme une publication déjà effectuée.

**Aucun ARK ni contour ajouté au site dans cette PR** ; aucune correction des libellés Pactols sans nouvelle version RDF.
