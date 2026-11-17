# Corse — publication de 360 correspondances Pactols–COG 2026

**17 novembre 2026 — PR 100 ; publication documentaire sans validation géométrique ou historique.**

## Décisions et sources

Les **360 communes COG 2026 de Corse** (124 en Corse-du-Sud, 236 en Haute-Corse) disposent chacune d'une assertion `skos:exactMatch` univoque dans le RDF Pactols-Lieux Frantiq, confirmée par l'audit régional PR 97 et le registre PR 98.

- Source : `frantiq/PACTOLS` commit `69bf9697e24cefd645a69465bbd271702786285a`, `Pactols_Lieux_th17_20260722.rdf` SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.
- Référence : COG Insee `v_commune_2026.csv`, contrôlé à SHA-256 par `recuperer_cog_2026.py`.
- Registre : `recette/lieux/CORSE-VALIDATIONS-PACTOLS-COG-2026.csv` (360 lignes, codes et ARK uniques). Une CI régénère **octet à octet** ce CSV depuis les deux sources épinglées.
- Index GitHub Pages : `docs/data/lieux-chronologie/pactols-corse-2026.json` ; schéma `adlfi.lieux.pactols.corse.2026.public.v1`, **360 couples**.

## Choix de structure

L'index de validation Pactols est **un fichier séparé** du COG historique `docs/data/lieux-chronologie/cog-corse.json`, qui demeure strictement identique à sa recette initiale. Le moteur `lieux-corse-pactols.js` contrôle la concordance code/nom avec les 360 communes actives au 1er janvier 2026, le statut des décisions, la famille d'URI `geo/commune`, la provenance et l'unicité des ARK.

Les 360 liens sont ajoutés à **l'index de recherche textuelle** du module Lieux (noms, codes, ARK), et à la **fiche communale** (nom Pactols, lien ARK, précision de validité 2026). Un lien validé en 2026 **n'est jamais retranscrit** sur les codes antérieurs `20xxx` de la Corse avant 1976, sur les épisodes de fusion, sur la surface des contours, ni sur les dates des événements.

L'index des **212 communes ultramarines** et les **103 autorités déjà validées en PACA** demeurent inchangés : ces ensembles ont un périmètre et une provenance distincts. La publication corse n'affirme ni couverture nationale des lieux des notices AdlFI ni validation de 360 géométries.

## Recette et garanties

La CI `lieux-corse-publication-360-2026.yml` contrôle :

- le SHA-256 des sources Pactols et COG, l'égalité octet à octet du CSV reconstruit et du registre archivé ;
- les 360 couples publiés, leur unicité, les statuts et le manifeste, par `verifier_publication_pactols_corse_2026.py` ;
- l'absence de mutation de la chronologie COG et des données topologiques ;
- la recherche d'un ARK corse et l'affichage de sa fiche dans Chromium, y compris avec une année antérieure à 1976 ;
- les contrôles généraux du site et la recette navigateur Lieux préexistante.

La recette temporelle de l'index COG conserve ses conditions d'origine (`alignements_Pactols_COG_valides_2026=[]` pour la couche historique corse) : la publication est apportée par la **jointure documentaire séparée** dans le navigateur et non par réécriture des états COG.

## Suite

Après mise en ligne de la Corse, reprendre la Bourgogne-Franche-Comté et les Pays de la Loire. Avant d'arbitrer les cinq communes classées « sans exactMatch » à URI de code dans la PR 97, élargir l'analyse aux URI Insee pérennes de forme UUID (ex. Val-d'Usiers) et vérifier leur résolution officielle dans le graphe RDF Insee, sans considérer une simple homonymie comme une équivalence.
