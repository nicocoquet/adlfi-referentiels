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

## Résultats de l'audit COG officiel

La [CI n°44080395783](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44080395783) a vérifié les six sources INSEE SHA-256 et deux extractions identiques. Résultats :

| Épisodes code–libellé COG (communes actuelles) | Nombre | Début COG |
| --- | ---: | --- |
| Les 32 communes autres que Kouaoua | **32** | **30 mars 1969** |
| Kouaoua, code `98833` | **1** | **25 avril 1995** |
| Total | **33** | 33 épisodes, sans fin inscrite dans cette série |
| Autres codes historiques `988` non courants | **0** | Aucun dans la série consultée |

La commune de **Canala (`98804`)** conserve un épisode de code depuis le **30 mars 1969**, alors que **Kouaoua (`98833`)** apparaît au **25 avril 1995**, date correspondant à sa division légale documentée par la [notice INSEE](https://www.insee.fr/fr/information/7929495).

Le contrôle du code courant de **Poya (`98827`)** est également positif. Selon la loi organique de 1999, la commune relève **à la fois des provinces Nord et Sud** : la recette interdit donc son rattachement provincial univoque. Les **huit aires coutumières** restent un niveau totalement indépendant.

Aucun contour provincial, géométrie historique ni correspondance Pactols n'a été déduit de ces constats.

Le workflow réalise deux extractions JSON reproductibles et archive le rapport hors `docs/`. **Zéro nouveau contour, zéro ARK Pactols, zéro succession automatique ; aucune nouvelle entité publique dans ce lot.**
