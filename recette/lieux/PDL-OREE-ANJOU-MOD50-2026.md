# Orée d’Anjou (49126) — alignement 2026 par transfert de chef-lieu MOD50

**Décision documentée du 18 novembre 2026, hors correction automatique du RDF Pactols.**

Le concept Pactols [`26678/pcrtS50omR9Tb5`](https://ark.frantiq.fr/ark:/26678/pcrtS50omR9Tb5), dont le `skos:prefLabel` est « Orée d'Anjou », contient un `skos:exactMatch` vers l'URI INSEE **`http://id.insee.fr/geo/commune/49069`**. Ce lien n'est pas erroné pour la période antérieure : le COG documente que la commune nouvelle d'Orée d'Anjou porte le code `49069` entre le **15 décembre 2015** et le **31 décembre 2024**.

Au **1er janvier 2025**, le COG enregistre un mouvement `MOD50` **`49069 → 49126`**, sans changement de libellé ni de type `COM`. La [liste de modalités du COG 2025, Insee](https://www.insee.fr/fr/information/8377252) définit explicitement le code **50** : « Changement de code dû à un transfert de chef-lieu ». Ce mouvement n'est **pas une création de commune nouvelle (MOD32)**. Le [dossier INSEE 2026 d'Orée d'Anjou](https://www.insee.fr/fr/statistiques/2011101?geo=COM-49126) confirme le code actuel `49126`, tout en conservant les événements d'ancienne commune déléguée associés à `49069`.

Le [concept Pactols de Drain `26678/pcrtlzVsRTHJSP`](https://ark.frantiq.fr/ark:/26678/pcrtlzVsRTHJSP), dont l'`exactMatch` porte le code `49126` réutilisé depuis 2025, reste une **ancienne autorité distincte**, jamais retenue comme ARK de la commune nouvelle.

**Choix éditorial :** valider la correspondance `pcrtS50omR9Tb5 ↔ 49126` **pour 2026**, avec deux preuves explicites chaînées : le `skos:exactMatch` Pactols au code `49069` et l'événement officiel COG `MOD50` vers `49126`. Le résultat ne doit pas être présenté comme si Pactols contenait directement un `exactMatch` vers `49126`. Aucune équivalence ARK–ARK, nouvelle géométrie ou reconstitution historique supplémentaire.

## Distinction essentielle — Les Hauts-d'Anjou

Le concept Pactols `26678/pcrtJmNskrfHiK` porte « Les Hauts d'Anjou » et un `exactMatch` INSEE `49065`, **correct pour la commune nouvelle créée le 15 décembre 2016**. Le COG et [l'Insee](https://www.insee.fr/fr/statistiques/2011101?geo=COM-49080) attestent qu'une **autre commune nouvelle**, « Les Hauts-d'Anjou », naît le **1er janvier 2019** par réunion de la première et de Châteauneuf-sur-Sarthe, sous le code `49080`. Les deux graphies ne sont pas interchangeables du point de vue de l'identité administrative. Contrairement à Orée d'Anjou, ce passage est un **MOD32** : le concept 2016 ne doit pas être promu vers `49080` sans preuve propre à la commune de 2019.

**Effet après réussite des contrôles :** ajout d'un alignement 2026, couverture **1 195 / 1 228**, **33 exceptions**. Le présent dossier conserve expressément la distinction entre preuve RDF et décision éditoriale utilisant le COG.
