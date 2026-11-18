# Pays de la Loire — publication de 17 alignements indirects Pactols–Wikidata–COG 2026

**Arbitrage éditorial du 18 novembre 2026, à confirmer par les tests de la PR.** Le référentiel PDL compte avant ce lot **1 195 correspondances publiées / 1 228 communes** et 33 exceptions. La [PR 143](https://github.com/nicocoquet/adlfi-referentiels/pull/143) a qualifié 17 concepts Pactols contemporains dépourvus de tout `skos:exactMatch` INSEE direct.

## Chaîne de preuve acceptée pour le millésime 2026

1. **Pactols** : le concept est unique dans le snapshot RDF th17 épinglé (`Pactols_Lieux_th17_20260722.rdf`, commit `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`). Il porte un `prefLabel` français compatible avec le COG 2026 et un `skos:exactMatch` vers **un élément Wikidata précis**, sans autre `exactMatch` contradictoire ni dépréciation/remplacement.
2. **Wikidata, révisions figées** : l'élément Q possède **exactement un code INSEE actif au 1er janvier 2026** dans `P374`, égal au code COG, un type `P31=Q484170` (commune française) et une date de création `P571` concordante. La preuve est conservée pour les 17 entités dans [PDL-17-WIKIDATA-P374-2026.json](PDL-17-WIKIDATA-P374-2026.json), avec `lastrevid` et URL de révision `oldid`. L'audit a comparé en CI le snapshot Wikidata récupéré à ce registre, puis régénéré deux preuves identiques.
3. **COG de l'Insee, édition 2026** : la commune `COM` existe au 1er janvier 2026 sous le code et le libellé indiqués, avec épisode antérieur séparé du même code et événement officiel `MOD32` à la date de création. Le COG a été dérivé du CSV officiel et validé lors des PR antérieures ; la présente PR utilise sa copie versionnée, sans prétendre à un nouveau téléchargement.

La conclusion est une **correspondance éditoriale à portée 2026**. Elle n'affirme **pas** que Pactols possède un `skos:exactMatch` direct vers le code INSEE : le chemin est `Pactols skos:exactMatch Wikidata → Wikidata P374 → COG 2026`. Les concepts des **anciennes communes** restent distincts : aucun `owl:sameAs` entre ARK et aucune rétroprojection sur les états antérieurs.

## Effet après réussite de la recette

Le fichier `docs/data/lieux-chronologie/pactols-pdl-wikidata-p374-2026.json` ajoute **17** correspondances aux **1 195** existantes, pour un total de **1 212 / 1 228**, soit **16 exceptions**. Chaque fiche doit expliquer la preuve médiatisée par Wikidata, sans attribuer à Pactols un code absent de son RDF. Aucune géométrie ni transition historique n'est ajoutée.

Le lot couvre Ancenis-Saint-Géréon, Bellevigne-les-Châteaux, Huillé-Lézigné, Saint-Léger-de-Linières, Rives-du-Loir-en-Anjou, Bierné-les-Villages, Château-Gontier-sur-Mayenne, Gennes-Longuefuye, La Roche-Neuville, Vimartin-sur-Orthe, Cherré-Au, Val-d'Étangson, Bernay-Neuvy-en-Champagne, L'Aiguillon-la-Presqu'île, Rives-d'Autise, Les Velluire-sur-Vendée et Chanverrie.

Les **16 exceptions** qui restent hors lot sont : Les Hauts-d’Anjou 2019 (`49080`, identité distincte de celle de 2016), cinq communes sans concept contemporain identifié (`72155`, `72382`, `85076`, `85223`, `85289`), neuf collisions historiques `49018`, `49160`, `49176`, `49244`, `53161`, `53255`, `72137`, `72176`, `85084`, et Rives-du-Fougerais `85292`.

**Contrôles obligatoires :** double génération JSON identique au fichier versionné, contrôle de tous les QID/révisions, des dates COG et MOD32, unicité globale 1 212, ancienne commune non promue, recherche et fiches Chromium, non-régressions PDL/Corse/BFC/PACA/DROM.

## Sources d'exemple

- [Insee : Ancenis-Saint-Géréon (44003)](https://www.insee.fr/fr/metadonnees/geographie/commune/44003-ancenis-saint-gereon).
- [Wikidata Q57208924, identité et code 44003](https://www.wikidata.org/wiki/Q57208924).
- [Insee : Bellevigne-les-Châteaux (49060)](https://www.insee.fr/fr/metadonnees/geographie/commune/49060-bellevigne-les-chateaux).
- [Wikidata Q58839998, identité et code 49060](https://www.wikidata.org/wiki/Q58839998).

Après la consolidation des exceptions régionales restantes, la priorité suivante est **la refonte de l'interface graphique du référentiel Lieux selon les idées de l'éditeur**.
