# Pays de la Loire — publication du lot 02 de 45 communes nouvelles au COG 2026

**Décision documentaire proposée (18 novembre 2026), après préqualification de la PR 139.**

La recette reproductible a isolé **45 dossiers** qui satisfont tous aux critères exigeants de `scripts/prequalifier_pdl_lot02_2026.py`. Chaque alignement s'appuie sur deux concepts Pactols distincts : celui de la commune nouvelle actuellement désignée au COG 2026, et celui de l'ancienne commune dont le code INSEE a été conservé. L'ancienne commune apparaît séparément dans un mouvement `MOD32` **COM vers COMD** ; la nouvelle commune est attestée au même jour en `COM`. Le libellé de l'ARK courant est strictement celui de la commune COG 2026.

**Chaîne de preuve :** Pactols-Lieux th17 du 22 juillet 2026, commit Frantiq `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7` ; COG INSEE 2026 épinglé, `docs/data/lieux-chronologie/cog-pdl.json`, colonnes de mouvements et épisodes. Toutes les URI INSEE des deux concepts, la dépréciation, les remplacements éventuels et la concordance des dates sont contrôlés **individuellement** pendant la génération. Les autres `exactMatch` externes n'établissent pas par eux-mêmes une identité.

Quelques corroborations officielles indépendantes : [Beaupréau-en-Mauges](https://www.insee.fr/fr/statistiques/2011101?geo=COM-49023), [Vallons-de-l'Erdre](https://www.insee.fr/fr/statistiques/2011101?geo=COM-44180), [Noyant-Villages](https://www.insee.fr/fr/statistiques/2011101?geo=COM-49228).

L'index `docs/data/lieux-chronologie/pactols-pdl-communes-nouvelles-lot02-2026.json` conserve, pour chaque commune, l'ARK courant, l'ARK ancien non promu, leurs libellés, le code INSEE, l'événement COG et la provenance. Il est **additionnel** aux quatre publications précédentes : 1 140 + 3 + 5 + 1 + **45 = 1 194** correspondances sur 1 228, avec **34 exceptions** résiduelles.

Les neuf collisions écartées de la publication sont : Baugé-en-Anjou (`49018`), Ingrandes-le-Fresne-sur-Loire (`49160`), Le Lion-d'Angers (`49176`), Mauges-sur-Loire (`49244`), Montsûrs (`53161`), Sainte-Suzanne-et-Chammes (`53255`), Villeneuve-en-Perseigne (`72137`), Le Lude (`72176`) et Essarts-en-Bocage (`85084`). Les **24 divergences de libellé/statut/URI** et **Rives-du-Fougerais (`85292`)** demeurent également hors validation.

Cette publication ne doit créer **aucune relation d'équivalence entre ARK**, aucun épisode administratif ni géométrie historiques. Le moteur du site présente la preuve pour 2026 uniquement ; la frise COG reste indépendante. Il faut contrôler l'index dans Chromium et les non-régressions interrégionales avant de fusionner.

**Après consolidation des exceptions Pays de la Loire**, le chantier basculera sur les nouvelles idées d'interface graphique du référentiel Lieux.
