# Nouvelle-Calédonie — instruction COG 2026, provinces et aires coutumières

**17 novembre 2026 — audit documentaire préalable, sans publication d'ARK ni géométrie.**

## Unités distinctes

La [codification INSEE des collectivités et territoires d'outre-mer](https://www.insee.fr/fr/information/7929495) atteste **33 communes en Nouvelle-Calédonie**, dont **Kouaoua**, créée en **1995** par division de Canala. Elles sont déjà présentes dans l'index COG du module Lieux, mais aucune correspondance Pactols communale de Nouvelle-Calédonie n'est encore validée.

La [loi organique n° 99-209 du 19 mars 1999](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000393606/) distingue **trois provinces** (Nord, Sud, Îles Loyauté) et **huit aires coutumières**. **La commune de Poya est explicitement répartie entre les provinces Nord et Sud.** La catégorie `commune` n'a donc pas nécessairement un unique parent provincial au sens de la géométrie. Une table `code commune → code province` à valeur unique serait incorrecte pour Poya.

Les aires coutumières ne sont ni des subdivisions du COG identiques aux provinces ni des communes associées polynésiennes. Les tribus et districts coutumiers ne doivent pas être générés depuis les noms des communes sans source spécifique.

## Protocole

Le script `scripts/auditer_cog_nouvelle_caledonie_2026.py` croise les **six fichiers INSEE originaux COG 2026** épinglés SHA-256 :

- `v_comer_2026.csv` et `v_commune_comer_2026.csv` : la collectivité `988` et ses 33 communes actuelles ;
- `v_tom_depuis_1943.csv` et `v_commune_outremer_depuis_1943.csv` : épisodes code–libellé historiques, notamment **Canala / Kouaoua** ;
- `v_commune_2026.csv` et `v_commune_depuis_1943.csv` : contrôle d'absence de confusion avec les DROM.

Le rapport de recette distinguera :

1. **codes et libellés courants** ;
2. **épisodes COG anciens**, sans assimiler première date d'attestation COG et création juridique ;
3. **Poya à deux provinces**, à préserver avant toute construction d'une couche provinciale ;
4. **aires coutumières**, à instruire comme niveau séparé ;
5. **Pactols**, à auditer ultérieurement par `skos:exactMatch` explicite, sans homonymies supposées.

Le workflow réalise deux extractions JSON reproductibles et archive le rapport hors `docs/`. **Zéro nouveau contour, zéro ARK Pactols, zéro succession automatique ; aucune nouvelle entité publique dans ce lot.**
