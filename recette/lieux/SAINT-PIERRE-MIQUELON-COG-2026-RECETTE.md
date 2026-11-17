# Saint-Pierre-et-Miquelon — instruction des deux communes et de la collectivité (COG 2026)

**17 novembre 2026 — phase 1 : audit indépendant, non validant, non publié sous `docs/`.**

## Problème d'autorité

Le [COG Insee 2026](https://www.insee.fr/fr/information/8740222) enregistre deux **communes de la collectivité 975**, qui restent distinctes de l'identité administrative de la collectivité elle-même :

| Code COG 2026 | Type | Dénomination actuelle |
| --- | --- | --- |
| `975` | Collectivité d'outre-mer (COMER) | Saint-Pierre-et-Miquelon |
| `97501` | Commune | Miquelon-Langlade |
| `97502` | Commune | Saint-Pierre |

Les communes figurent déjà dans le **moteur de recherche ultramarin 2026** du module Lieux. Le fichier public actuel ne porte **aucun rapprochement Pactols validé** pour `97501` ou `97502`. Cette absence de décision ne démontre ni la présence ni l'absence de concepts Pactols dans l'export RDF ; l'analyse RDF devra être menée indépendamment de la qualification COG.

## Changements de statut de la collectivité ≠ création des communes

La [notice de codification de l'Insee consacrée aux collectivités d'outre-mer](https://www.insee.fr/fr/information/7929495) et [Légifrance, loi n° 85-595](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000693671/) attestent :

- **19 juillet 1976**, loi n° 76-664 : transformation en département d'outre-mer ;
- **11 juin 1985**, loi n° 85-595 : passage au statut de collectivité territoriale ;
- **28 mars 2003**, loi constitutionnelle n° 2003-276 : nouvelle catégorie des collectivités d'outre-mer, article 74 ;
- **21 février 2007**, loi organique n° 2007-223 : actualisation du statut et des institutions.

**Ces dates désignent ici les textes juridiques** et non nécessairement les dates d'effet retenues dans les enregistrements historiques du COG. Aucune de ces lois ne prouve en elle-même une modification des limites ou des identités des deux communes.

Il faut distinguer **au moins trois temporalités** : les périodes `code–libellé` du COG, les étapes du statut juridique de la collectivité, et les éventuelles géométries datées. La frise de l'interface représente uniquement des **états au 1er janvier** : elle ne doit pas escamoter le régime DOM de 1976–1985.

## Sources officielles mobilisées

Le script `scripts/auditer_cog_saint_pierre_miquelon_2026.py` lit six CSV de l'[archive officielle COG Insee 2026](https://www.insee.fr/fr/information/8740222), avec SHA-256 strictement épinglés et vérifiés en CI.

| Fichier Insee | Utilisation |
| --- | --- |
| `v_comer_2026.csv` | Collectivité 975 actuelle |
| `v_commune_comer_2026.csv` | Les deux communes COMER actuelles |
| `v_tom_depuis_1943.csv` | Périodes documentaires de la collectivité 975 |
| `v_commune_outremer_depuis_1943.csv` | Épisodes communaux en série COMER |
| `v_commune_depuis_1943.csv` | Contrôle d'éventuels épisodes DOM dans la série française |
| `v_commune_2026.csv` | Contrôle du snapshot officiel communal DROM et métropolitain |

**Méthode de recette** : le workflow télécharge et vérifie les six CSV, génère deux rapports JSON pour contrôler la reproductibilité, imprime les épisodes exacts de la collectivité et des communes, et archive le rapport **hors GitHub Pages**.

### Décisions interdites à ce stade

- **0** correspondance Pactols–COG nouvellement validée ;
- **0** succession d'autorités déduite d'un changement de statut ;
- **0** géométrie historique restituée ;
- **0** rétroprojection du COG 2026 sur les états antérieurs.

**La phase 2 — intégration des épisodes à la frise et aux fiches — sera préparée seulement après examen des dates et périodes réellement présentes dans les six fichiers Insee**. Cette vérification évitera de fabriquer une continuité territoriale artificielle entre les épisodes COMER, DOM et COMER.
