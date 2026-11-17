# Bourgogne-Franche-Comté — publication des 3 614 ARK Pactols au COG 2026

17 novembre 2026. Lot métropolitain préparé après la Corse ; 71 exceptions conservées.

## Sources et validation

- COG Insee 2026, TYPECOM=COM, REG=27 : **3 685 communes**.
- RDF Pactols th17 du 22 juillet 2026, commit 69bf9697e24cefd645a69465bbd271702786285a, SHA-256 3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7.
- PR 101 : **26 concepts avec exactMatch INSEE UUID**, dont seul Val-d’Usiers (25060) est candidat BFC. Aucune résolution automatique de code depuis l'UUID.
- PR 102 : **3 614 liens éligibles**, avec ARK et URI de code uniques, sans URI INSEE supplémentaire contradictoire ; CSV SHA-256 **494dad4ddbf562b96a0b37a5e10ea56ba2deff1289255bb7e35bcdecefa5d0c5**.

## Index indépendant du COG historique

- Registre : recette/lieux/BFC-VALIDATIONS-PACTOLS-COG-2026.csv, 3 614 décisions VALIDE_ADLFI_2026 par règle.
- Index public : docs/data/lieux-chronologie/pactols-bfc-2026.json, schéma adlfi.lieux.pactols.bfc.2026.public.v1.
- Validateur JS : docs/assets/lieux-bfc-pactols.js, contrôle de la cardinalité COG et du millésime, univocité codes/ARK, provenance et rejet de Val-d'Usiers.
- Moteur de recherche : docs/assets/lieux-multiechelon.js, recherche par nom/code/ARK, fiche avec lien Pactols explicitement validé pour **2026 seulement**.

**71 communes exclues** : 44 cas de plusieurs ARK, 26 divergences et Val-d'Usiers (URI UUID non résolue). Leurs fiches COG restent accessibles sans ARK Pactols approuvé. Ni les épisodes historiques, ni les événements, ni les GeoJSON ne sont changés. Aucune géométrie historique ni équivalence rétroactive n'est déduite.

## Procédure de recette

Le workflow lieux-bfc-publication-3614-2026.yml :

1. Régénère deux fois le registre CSV et le JSON public depuis les sources officielles à SHA-256 épinglé.
2. Vérifie les égalités octet à octet, le SHA de la PR 102, l'unicité des identifiants et les 71 exclusions.
3. Contrôle le manifeste, le COG historique et les tests de non-régression Corse et BFC.
4. Exécute Chromium sur recherche ARK, fiche communale, frise antérieure et exception Val-d'Usiers.
5. Versionne les sorties **dans la branche de PR seulement après succès des tests**, sans écriture directe sur main.

La PR ne sera fusionnée qu'après réussite de la CI sur le code et les deux fichiers générés. Cette publication qualifie des alignements documentaires Pactols–COG 2026, et non la couverture des 9 928 autorités effectivement utilisées dans les notices.

## Résultats de la recette réelle — 17 novembre 2026

- [CI de génération et navigateur n°44176179708](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44176179708) : réussie, avec les deux fichiers ajoutés à la branche de PR après contrôle.
- **3 614 codes INSEE et 3 614 ARK uniques**, 71 exceptions exclues, dont Val-d’Usiers 25060.
- CSV régénéré deux fois, SHA-256 **494dad4ddbf562b96a0b37a5e10ea56ba2deff1289255bb7e35bcdecefa5d0c5** ; JSON régénéré deux fois, 1 146 086 octets.
- Contrôles Python, Node, quatre chronologies et Chromium : **BFC_3614_INDEX_OK**, **BFC_3614_NAVIGATEUR_OK**, **CORSE_360_NAVIGATEUR_OK**.
- Artefact : bfc-3614-registre-et-index-verifies-2026.

Ces résultats ne qualifient aucun contour historique et n’ajoutent aucun ARK aux 71 communes en instruction.
