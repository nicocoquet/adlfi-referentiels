# Pays de la Loire — qualification du reliquat documentaire 2026

**18 novembre 2026 — consolidation non validante en vue de la clôture régionale.** État public : **1 217 / 1 228 (99,1 %), 11 exceptions** après PR #148. Cette pièce ne valide aucun nouvel ARK et ne modifie pas l'index.

## Sept exceptions autres que les quatre collisions historiques

| COG 2026 | Commune | Situation administrative établie | Statut dans le snapshot Pactols th17 et décision |
| --- | --- | --- | --- |
| 49080 | Les Hauts-d'Anjou | Nouvelle création **01/01/2019** des Hauts d'Anjou (49065) et Châteauneuf-sur-Sarthe (49080) | ARK `26678/pcrtJmNskrfHiK` qualifié pour la commune précédente (49065) : **ne pas reporter** sur 49080 ; rechercher un concept 2019 propre |
| 85292 | Rives-du-Fougerais | Nouvelle création **01/01/2024** ; code actuel 85292 | Loterre possède `skos:exactMatch` vers UUID officiel INSEE 85292, mais mentionne **85041** (Cezais) ; aucun lien Pactols → Loterre démontré ; **ne pas promouvoir** `26678/pcrtjr01c5sg25ngf5hq8898` sur simple concordance de libellé ; correction de source à demander |
| 72155 | Laigné-Saint-Gervais | Nouvelle création **01/01/2025** : Laigné-en-Belin (72155) + Saint-Gervais-en-Belin (72287) | **Aucun concept contemporain identifié** dans l'audit RDF th17 ; ne pas réutiliser l'autorité de Laigné-en-Belin |
| 72382 | Val-de-la-Hune | Nouvelle création **01/01/2025** : Saint-Mars-de-Locquenay (72298) + Volnay (72382) | **Aucun concept contemporain identifié** dans l'audit RDF th17 ; ne pas réutiliser Volnay |
| 85076 | Cugand-la-Bernardière | Nouvelle création **01/01/2025** : La Bernardière (85021) + Cugand (85076) | **Aucun concept contemporain identifié** dans l'audit RDF th17 ; ne pas réutiliser Cugand |
| 85223 | Saint-Jean-d'Hermine | Nouvelle création **01/01/2025** : Sainte-Hermine (85223) + Saint-Jean-de-Beugné (85233) | **Aucun concept contemporain identifié** dans l'audit RDF th17 ; ne pas réutiliser Sainte-Hermine |
| 85289 | Terval | Nouvelle création **01/01/2023** : Breuil-Barret (85037), La Chapelle-aux-Lys (85053), La Tardière (85289) | **Aucun concept contemporain identifié** dans l'audit RDF th17 ; ne pas réutiliser La Tardière |

**Important :** « Aucun concept identifié » signifie **absence de candidat qualifié dans le snapshot RDF contrôlé le 22 juillet 2026**, pas affirmation que Pactols ne contient aucune autorité au jour de rédaction. Une future version RDF peut corriger cette lacune.

## Sources officielles

- Insee, [Les Hauts-d'Anjou 49080](https://www.insee.fr/fr/statistiques/2011101?geo=COM-49080)
- Insee, [Rives-du-Fougerais 85292](https://www.insee.fr/fr/metadonnees/geographie/commune/85292-rives-du-fougerais) ; [rapport de preuve UUID et anomalie de source](PDL-RIVES-FOUGERAIS-LOTERRE-INSEE-2026.json)
- Insee, [Laigné-Saint-Gervais 72155](https://www.insee.fr/fr/statistiques/2011101?geo=COM-72155)
- Insee, [Val-de-la-Hune 72382](https://www.insee.fr/fr/statistiques/2011101?geo=COM-72382)
- Insee, [Cugand-la-Bernardière 85076](https://www.insee.fr/fr/statistiques/2011101?geo=COM-85076)
- Insee, [Saint-Jean-d'Hermine 85223](https://www.insee.fr/fr/statistiques/2011101?geo=COM-85223)
- Insee, [Terval 85289](https://www.insee.fr/fr/statistiques/2011101?geo=COM-85289)
- Loterre, [Rives-du-Fougerais, variante erronée 85041](https://loterre.istex.fr/D63/fr/page/-G704CG2Q-F?clang=fr).

## Décisions de clôture proposées

1. **Conserver les cinq absences** comme données à demander/ajouter à Pactols plutôt que fabriquer des ARK sur les anciennes communes.
2. **Les Hauts-d'Anjou** : demande d'autorité/rectification fondée sur le changement d'identité de 2019, non simple correction du code `49065` en `49080`.
3. **Rives-du-Fougerais** : signaler à Loterre/Frantiq l'anomalie `85041` ; ne pas prétendre que la preuve UUID Loterre est un `exactMatch` du concept Pactols.
4. **Quatre collisions historiques** : suivre les pièces [Lion-d'Angers/Le Lude](PDL-LION-LUDE-DESAMBIGUISATION-2026.md) et [Baugé/Montsûrs](PDL-BAUGE-MONTSURS-ETATS-2026.md). L'extraction RDF et le contrôle des identifiants externes restent nécessaires avant un éventuel alignement supplémentaire.
5. **Arrêt de la phase documentaire** possible sans 100 %, sous réserve de recetter la PR, de contrôler que le total et le registre des onze codes restent cohérents, et de mettre à jour le dossier #130. La clôture ne vaut pas clôture des géométries historiques.

**Méthode :** les créations/dates ci-dessus ont été vérifiées via l'Insee ; les statuts Pactols sont ceux des audits du RDF épinglé **antérieurs**, non une nouvelle exécution du RDF dans cette PR. Zéro alignement, géométrie ou succession ajouté au référentiel public.

**Suite de projet :** interface web d'exposition/navigation Lieux : hiérarchie région/département/commune/arrondissement municipal, navigation temporelle, fiches d'autorité avec état de preuve et géométries historiques qualifiées.
