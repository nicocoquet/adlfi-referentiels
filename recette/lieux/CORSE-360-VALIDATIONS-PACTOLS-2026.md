# Corse — registre probatoire de 360 correspondances Pactols–COG 2026

**17 novembre 2026 — validation éditoriale par règle, sans publication dans l'interface.**

## Socle

La PR 97 a vérifié que les **360 communes COG 2026 de Corse (région 94)** disposent toutes d'un `skos:exactMatch` RDF univoque vers une URI Insee `geo/commune/{code}` ; les 360 concepts sont non dépréciés, non remplacés, et les libellés sont compatibles. La règle [Pactols–COG](POLITIQUE-ALIGNEMENT-PACTOLS-COG.md) du 16 novembre permet leur validation **au seul millésime 2026**, avec provenance conservée.

Le script `scripts/preparer_validations_pactols_corse_2026.py` contrôle chaque ligne avant de produire un registre CSV de 360 lignes. Les codes corses `2A` et `2B` sont conservés comme chaînes alphanumériques ; la région est tirée du champ `REG=94` du COG, non des seuls préfixes.

## Provenance

- RDF Pactols-Lieux Frantiq : `Pactols_Lieux_th17_20260722.rdf`, commit `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.
- COG INSEE `v_commune_2026.csv`, SHA-256 `7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3`.
- État des validations : `VALIDE_ADLFI_2026`, décision `REGLE_EXACTMATCH_UNIVOQUE`, portée `2026-01-01`.
- La CI `lieux-corse-validations-pactols-2026.yml` produit **deux CSV identiques**, vérifie unicité des 360 ARK et codes, conserve l'artefact de recette **hors `docs/`**.

## Distinction entre preuve et publication

Cette PR valide méthodiquement les couples identifiants 2026, mais **aucun ARK ne sera affiché dans le module Lieux tant que le registre n'aura pas été intégré par une recette de publication dédiée**. À cette étape : `publication_site=EN_ATTENTE_RECETTE_PUBLICATION`.

La Corse compte plusieurs évolutions administratives historiques déjà documentées dans le COG. La validation des identifiants pour 2026 **ne valide ni les formes anciennes, ni les successions, ni les géométries rétrospectives**. Les contours cartographiques existants ne sont pas modifiés.

## Suite

Après réussite de la CI et inspection du registre, préparer une PR de publication rattachant les 360 codes communaux 2026 à leurs ARK, avec tests de recherche et de navigation, sans modifier les couches géométriques ni les chronologies.

En parallèle, ouvrir une instruction méthodologique séparée sur les URI RDF Insee à identifiant UUID : notamment la ressource `http://id.insee.fr/geo/commune/52976ff6-5685-48c9-b468-7417ad44b653` signalée pour **Val-d'Usiers**, sans lui attribuer automatiquement le code `25060` avant vérification dans la source Insee. Les cinq absences d'`exactMatch` reconnues par le parseur de la PR 97 ne sont pas des absences définitivement attestées.
