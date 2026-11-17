# Pays de la Loire — préparation des 1 140 alignements Pactols–COG 2026

**Recette non publiée, 17 novembre 2026.**

La première analyse régionale PR 97 distingue **1 228 communes COG 2026** (région 52), dont **1 140 correspondances univoques éligibles**, **60 codes avec plusieurs ARK**, **24 divergences de libellé, statut ou URI**, **4 communes sans exactMatch** reconnu au format de code.

Quatre communes sans assertion de code dans le RDF épinglé :
- 44066 Grandchamp-des-Fontaines — candidat lexical non validant ;
- 85165 L'Oie — candidat lexical non validant ;
- 85212 Sainte-Florence — pas de candidat lexical identifié dans le premier parseur ;
- 85292 Rives-du-Fougerais — candidat lexical non validant.

## Méthode

- Sources : Pactols-Lieux RDF th17 du 22 juillet 2026, commit 69bf9697e24cefd645a69465bbd271702786285a, SHA-256 3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7 ; COG Insee 2026, fichier v_commune_2026.csv SHA-256 7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3.
- Sélection stricte sur TYPECOM=COM et REG=52. Aucune identité géographique ancienne n'est déduite du préfixe du code.
- Pour les 1 140 liens candidats, vérification supplémentaire dans **tout le RDF brut** de l'absence d'autres exactMatch vers id.insee.fr/geo, notamment les URI UUID non reconnues par l'audit initial.
- Identifiants Pactols et codes communaux uniques ; CSV de décisions avec provenance et portée 2026, statut VALIDE_ADLFI_2026 **par règle**.
- Les **88 autres communes** sont consignées à part dans un rapport JSON avec le statut NON_PRISE ; elles ne sont ni validées ni publiées.

Les 22 collisions historiques de codes à instruire dans le chantier PDL et les mouvements de communes nouvelles demeurent distincts de ces décisions d'identité **2026**.

La CI produit deux exemplaires identiques octet à octet du CSV et des exceptions ; elle ne modifie aucun fichier dans docs, aucun contour et aucun épisode COG. La publication des couples approuvés fera l'objet d'une PR distincte, après vérification des résultats réels.

## Recette réelle — 17 novembre 2026

La [CI n°44179130324](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44179130324) est réussie, comme la [CI générale n°44179130427](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44179130427).

- **1 140** couples générés et contrôlés à partir des sources épinglées.
- **88** exceptions exclues (60 ARK multiples, 24 divergences, quatre codes sans assertion) ; aucune validation ou géométrie inférée.
- Deux CSV identiques, SHA-256 **81c49e32e5a443a1dd2e9f40e2d82c842a72ab1f82d81833fd51f02ae9d71335**.
- Test additionnel sur toutes les URI INSEE de chacun des 1 140 concepts réussi ; quatre tests locaux PDL et sept tests régionaux réussis.
- Artefact Actions : recette-pdl-1140-pactols-cog-2026 (CSV et rapport JSON d'exceptions).
