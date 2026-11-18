# Pays de la Loire — trois communes nouvelles aux ARK Pactols distincts

**Publication 2026 proposée, 18 novembre 2026.** À partir du diagnostic historique de la [PR 145](https://github.com/nicocoquet/adlfi-referentiels/pull/145), trois communes nouvelles présentent des preuves convergentes particulièrement précises : `skos:exactMatch` vers le code COG de la commune en 2026, `skos:prefLabel` strictement contemporain, notes d'histoire d'origine Insee dans Pactols et création `MOD32` au même jour dans le COG. L'ancienne commune est également identifiée dans le RDF par **un autre ARK**, avec le même code COG réutilisé mais un libellé historique différent.

| Code | Commune nouvelle en 2026 | Création COG | ARK Pactols de la commune nouvelle | Ancienne commune et ARK distinct |
|---|---|---|---|---|
| `49244` | Mauges-sur-Loire | 15 décembre 2015 | `26678/pcrtVBIl6UNl1S` | La Pommeraye — `26678/pcrtE0bVL7JsdM` |
| `53255` | Sainte-Suzanne-et-Chammes | 1er janvier 2016 | `26678/pcrtwUykeFf31u` | Sainte-Suzanne — `26678/pcrts0lDLWcVyJ` |
| `72137` | Villeneuve-en-Perseigne | 1er janvier 2015 | `26678/pcrtoVf9Ovfyy7` | La Fresnaye-sur-Chédouet — `26678/pcrtg6rwdnGM9r` |

Pour Villeneuve-en-Perseigne, le concept historique Pactols porte le libellé « Fresnaye-sur-Chédouet », sans l'article « La » du COG. Cette variation est **qualifiée explicitement pour ce seul ARK**, et non acceptée comme règle générale.

**Sources :** `Pactols_Lieux_th17_20260722.rdf`, commit Frantiq `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7` ; chronologie PDL `docs/data/lieux-chronologie/cog-pdl.json`, dérivée du COG 2026 déjà validé dans le projet. [Insee, Mauges-sur-Loire](https://www.insee.fr/fr/statistiques/2011101?geo=COM-49244) ; [Sainte-Suzanne-et-Chammes](https://www.insee.fr/fr/statistiques/2011101?geo=COM-53255) ; [Villeneuve-en-Perseigne](https://www.insee.fr/fr/statistiques/2011101?geo=COM-72137).

**Exclusions :** les six autres collisions historiques demeurent ouvertes : Baugé-en-Anjou, Ingrandes-le-Fresne-sur-Loire, Le Lion-d'Angers, Montsûrs, Le Lude et Essarts-en-Bocage. Sont également ouverts les cinq cas sans autorité contemporaine identifiée, Les Hauts-d'Anjou (concept 2016 distinct de 2019) et Rives-du-Fougerais.

Le générateur `scripts/publier_pdl_trois_collisions_2026.py` exige une double correspondance ARK/URI, les deux épisodes COM, les mouvements MOD32 et COM→COMD ainsi que la note historique dans le concept contemporain. Une validation réussie augmente la couverture de **1 212 à 1 215 / 1 228**, laisse **13 exceptions**, et ne crée **aucune géométrie ni relation d'équivalence historique**.
