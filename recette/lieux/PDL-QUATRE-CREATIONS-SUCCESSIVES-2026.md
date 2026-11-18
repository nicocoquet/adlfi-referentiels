# Pays de la Loire — quatre créations successives à ARK Pactols multiples

**Instruction non validante.** Sources : RDF Pactols-Lieux th17 épinglé (22 juillet 2026, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`) et mouvements du COG INSEE 2026 archivés dans `docs/data/lieux-chronologie/cog-pdl.json`. L'analyse reste séparée de l'index 2026.

| Code | Commune actuelle | Créations successives MOD32 | Concepts Pactols en conflit | Diagnostic préalable |
|---|---|---|---|---|
| `49018` | Baugé-en-Anjou | 2013-01-01, 2016-01-01 | Baugé-en-Anjou `26678/crtw3s8jkTOZ8` ; Baugé `26678/pcrthdy1gGxlIV` | Même dénomination pour les créations de 2013 et 2016 : la définition du concept Baugé-en-Anjou fait référence à la création de 2013, et ne documente pas à elle seule le changement de périmètre de 2016 |
| `49092` | Chemillé-en-Anjou | 2013-01-01, 2015-12-15 | Chemillé `26678/pcrtL5GRFXn3Zs` ; Chemillé-Melay `26678/pcrtWU8rdgPSSH` ; Chemillé-en-Anjou `26678/pcrtzDf0WnnRyr` | Trois dénominations successives distinctes, dont un candidat portant explicitement le nom actuel ; vérification favorable à approfondir |
| `49160` | Ingrandes-le-Fresne-sur-Loire | 2016-01-01, 2024-01-01 | Ingrandes `26678/pcrtD9YKBK1v7E` ; Ingrandes-Le Fresne sur Loire `26678/pcrtQBSwT6fBDW` | Aucun de ces deux libellés ne désigne explicitement la commune nouvelle du 1er janvier 2024 ; ne pas assimiler les graphies de 2016 et de 2024 |
| `53161` | Montsûrs | 2017-01-01, 2019-01-01 | Montsûrs `26678/pcrt2VftxEe5uH` ; Montsûrs-Saint-Céneré `26678/pcrtzZXdqdUiXm` | Montsûrs est le nom de l'ancienne commune avant 2017 et de la nouvelle commune depuis 2019 ; sans portée chronologique explicite du concept, sa seule concordance lexicale ne suffit pas |

## Point structurel COG

Pour Baugé-en-Anjou, la table `periodes_com` conserve **un seul intervalle de libellé depuis 2013**, alors que `lignes_mouvements_cog` documente aussi une création MOD32 en 2016. C'est un rappel important : **un intervalle de libellé n'est pas un identifiant stable de l'entité administrative ou de son périmètre**. Aucune correction de chronologie ou géométrie ne doit être déduite de cette observation sans instruction des identités administratives.

Pour Montsûrs, la séquence de libellés **Montsûrs → Montsûrs-Saint-Céneré → Montsûrs** est formellement inscrite dans le COG. La réutilisation du nom est donc un risque d'alignement majeur.

## Suite proposée

Examiner séparément la pertinence de l'ARK Chemillé-en-Anjou pour la situation 2026, sans promesse de promotion immédiate. Pour Baugé-en-Anjou et Montsûrs, rechercher des preuves qui permettent de distinguer les deux phases de commune malgré la réutilisation du même nom/code. Pour Ingrandes, rechercher un concept Pactols propre à la création de 2024, plutôt que de transformer l'ARK de l'entité de 2016.

Le rapport de recette conserve **les neuf ARK**, leurs notes RDF, les épisodes communaux COG et les mouvements, sans nouvelle validation. **État public inchangé : 1 148 / 1 228 correspondances, 80 exceptions.** Suivi : #130 ; publication précédente : PR #136.
