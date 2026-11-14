# Pays de la Loire — instruction des 22 codes Insee partagés (14 novembre 2026)

**PR n°24, recette non validante.** Le rapprochement des 806 autorités Pactols a identifié **22 codes Insee déclarés chacun sur deux ARK différents** (44 ARK au total). Cette collision est un signal de qualification historique, non une preuve d'erreur de codification ou un motif de fusion des concepts.

## Quatre dossiers vérifiés sur les fiches historiques Insee

| Code | Concepts Pactols | Épisode(s) officiels documentés | Source |
| --- | --- | --- | --- |
| `44005` | Arthon-en-Retz / Chaumes-en-Retz | **2016-01-01** : création de Chaumes-en-Retz avec Arthon-en-Retz et Chéméré ; Arthon devient commune déléguée | https://www.insee.fr/fr/statistiques/2011101?geo=COM-44005 |
| `44087` | Machecoul / Machecoul-Saint-Même | **2016-01-01** : création de Machecoul-Saint-Même avec Machecoul et Saint-Même-le-Tenu ; Machecoul devient commune déléguée | https://www.insee.fr/fr/statistiques/2011101?geo=COM-44087 |
| `49018` | Baugé / Baugé-en-Anjou | **2013-01-01** : première commune nouvelle (Baugé + Montpollin, Pontigné, Saint-Martin-d'Arcé et Le Vieil-Baugé). **2016-01-01** : nouvelle opération de création/extension de Baugé-en-Anjou avec d'autres communes, dont Clefs-Val d'Anjou ; Baugé conserve son statut de déléguée | https://www.insee.fr/fr/statistiques/2011101?geo=COM-49018 |
| `49023` | Beaupréau / Beaupréau-en-Mauges | **2015-12-15** : création de Beaupréau-en-Mauges, regroupant dix anciennes communes dont Beaupréau, devenu commune déléguée | https://www.insee.fr/fr/statistiques/2011101?geo=COM-49023 |

**18 codes partagés supplémentaires restent à vérifier individuellement sur le fichier officiel `v_mvt_commune_2026.csv`.** Aucune date ni nature d'événement n'est inventée pour eux.

## Arbitrage de modélisation proposé

Un code seul ne constitue pas l'identifiant d'une autorité historique. On distingue dans le graphe :

- `ark_pactols` : identité du concept documentaire, immuable ;
- `code_insee` + `TYPECOM` + épisode daté : statut administratif attesté ;
- `evenement_cog` : opération officielle datée et ses entités avant/après ;
- `preuve` : fichier officiel Insee, millésime, URL et/ou empreinte ;
- `geometrie` : géométrie datée indépendamment, jamais héritée automatiquement par la commune nouvelle.

Le cas **Baugé-en-Anjou** démontre qu'il faut **plusieurs épisodes successifs pour un même code** ; une structure réduite à `ancien_libelle → nouveau_libelle` serait historiquement fausse.

## Livrables et limites

Les tableaux `collisions-codes-insee-22.csv`, `instruction-collisions-22.csv` et `rapport-instruction-collisions.json` sont fournis en archive dans la conversation. La vérification couvre 4 codes sur 22 ; le CSV complet des événements du COG 2026 n'est pas encore exploité sur l'ensemble des 806 autorités dans cette étape.

Le workflow du lot 25 a déjà démontré qu'il sait télécharger et vérifier les trois sources Insee : https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43602852827. Pour franchir l'étape suivante, il faudra intégrer l'inventaire 806 comme entrée de recette du workflow, puis faire tourner le croisement exhaustif.

**Aucun alignement Pactols–COG nouvellement validé et aucune géométrie historique publiée.**
