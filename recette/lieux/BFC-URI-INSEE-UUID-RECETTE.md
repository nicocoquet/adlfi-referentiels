# Bourgogne-Franche-Comté — recette des URI INSEE à UUID (17 novembre 2026)

## Justification

L'audit régional initial de la PR 97 qualifie 3 614 communes BFC comme éligibles par exactMatch vers une URI de code COG, 44 communes avec plusieurs ARK, 26 à libellé/statut/URI divergents et Val-d'Usiers (25060) comme sans exactMatch reconnu. Le parseur existant ne reconnaît que les URI INSEE terminées par un code : une assertion skos:exactMatch vers une URI UUID ne figure donc pas dans son contrôle d'univocité.

Le lien Pactols cité pour Val-d'Usiers est de la forme http://id.insee.fr/geo/commune/52976ff6-5685-48c9-b468-7417ad44b653. **La seule présence de ce lien ne suffit pas à établir que le référent INSEE correspond à la commune COM 25060 au 1er janvier 2026.** Le code 25060 était celui de Bians-les-Usiers, puis a été conservé pour la commune nouvelle de Val-d'Usiers créée le 1er janvier 2024 à partir de trois communes.

## Recette technique

Le script scripts/auditer_uris_insee_uuid_pactols_2026.py lit la version RDF Pactols th17 du 22 juillet 2026 et le COG 2026, tous deux vérifiés par SHA-256. Il inventoriera **tous les concepts possédant au moins un exactMatch vers une URI de commune INSEE à UUID**, même si le même concept possède aussi une URI INSEE à code. Pour chacun il conserve l'ARK, les libellés, les URI exactes, les autres exactMatch et les éventuels candidats en BFC par libellé ou code directement cité.

La sortie JSON est un artefact de recette, hors du répertoire GitHub Pages docs. Un champ code_cog_resolu_par_uuid demeure null pour tous les enregistrements. Les rapprochements de libellés ne sont jamais promus en alignements. Aucun JSON public, épisode COG, contour ou décision validée n'est modifié.


## Résultat du contrôle réel (17 novembre 2026)

Le workflow [44171980827](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44171980827) est réussi, de même que la CI générale [44171980781](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44171980781). Deux inventaires issus des sources épinglées sont identiques octet à octet :

- **50 556 concepts Pactols examinés** ;
- **26 concepts porteurs d'un skos:exactMatch INSEE UUID**, toutes zones ;
- **1 seul concept susceptible de concerner la BFC**, par libellé ou code INSEE direct : Val-d'Usiers ;
- **0 validation**, **0 contour**, **0 modification du site public**.

Dossier Val-d'Usiers : ARK 26678/pcrtksq5m3cwb846scr9wzkv ; URI INSEE exacte http://id.insee.fr/geo/commune/52976ff6-5685-48c9-b468-7417ad44b653 ; libellé Pactols Val-d'Usiers ; altLabels « 25060 (code Insee) » et « 25520 (code postal) » ; autre exactMatch Wikidata https://www.wikidata.org/wiki/Q123014277. Le code 25060 n'est **pas** directement cité sous la forme d'une URI de code dans les exactMatch de ce concept du snapshot.

Ces éléments convergents restent distincts de la résolution du **référent de l'URI UUID**. Aucune propriété officielle de l'objet RDF INSEE n'a encore été récupérée et contrôlée dans cette recette.

## Préflight avant publication BFC

1. Exécuter ce nouvel inventaire et relever les concepts susceptibles de concerner la Bourgogne-Franche-Comté, dont le cas Val-d'Usiers.
2. Résoudre les URI UUID dans les données RDF officielles de l'Insee : catégorie, identification du territoire, code(s), temporalité et éventuelle succession. Conserver les triplets et la provenance de cette résolution, sans déduire une identité du seul code 25060.
3. Recontrôler les 3 614 cas éligibles de l'audit PR 97 à la lumière de ces URI précédemment ignorées, sans supposer qu'ils conservent tous ce statut.
4. Produire ensuite un registre de décisions BFC ; publier les seuls liens validés dans un index Pactols séparé du graphe COG historique, sur le modèle corse.

## Sources

- Pactols-Lieux Frantiq, commit 69bf9697e24cefd645a69465bbd271702786285a, SHA-256 3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7.
- Insee, v_commune_2026.csv, SHA-256 7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3.
- https://rdf.insee.fr/geo/index.html : portail officiel RDF, avec réserve explicite sur son caractère expérimental et renvoi au site principal Insee en cas de divergence.
- https://www.insee.fr/fr/metadonnees/geographie/commune/25060-val-dusiers : création de Val-d'Usiers en 2024.
