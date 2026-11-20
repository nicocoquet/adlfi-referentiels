# Lieux — activation cartographique Normandie 2026

**20 novembre 2026 — proposition de publication de la cinquième région métropolitaine.**
Dossier de pilotage : [#152](https://github.com/nicocoquet/adlfi-referentiels/issues/152).

## Sources déjà versionnées et contrôlées

- [PR #161](https://github.com/nicocoquet/adlfi-referentiels/pull/161) : `cog-normandie.json` et `contours-2026-normandie.geojson`. **2 644 communes COG 2026** (`REG=28`, `TYPECOM=COM`), 2 644 contours Etalab/IGN de l'édition du **4 mai 2026**, généralisation 100 m, vérification GEOS individuelle. Le seul polygone source invalide, **Cahagnes 14120**, a été transcrit en `MultiPolygon` valide sans modification de surface ni d'emprise (preuve GEOS conservée). Aucune géométrie ancienne n'a été inférée.
- [PR #156](https://github.com/nicocoquet/adlfi-referentiels/pull/156) : neuf correspondances Pactols–COG validées pour 2026.
- [PR #160](https://github.com/nicocoquet/adlfi-referentiels/pull/160) : sept correspondances supplémentaires, trois dossiers suspendus.
- Total : **16 ARK contemporains validés pour 2026**, sans assimilation à l'ARK de l'ancienne commune. Les **4 dossiers suspendus** au cumul (Port-Bail-sur-Mer, Isigny-sur-Mer, Breteuil et Bourgvallées) ne deviennent **pas** des correspondances Pactols publiées.
- [PR #157](https://github.com/nicocoquet/adlfi-referentiels/pull/157) : chargement de géométries métropolitaines à la demande selon la fenêtre visible au zoom supérieur ou égal à 7.

## Comportement de l'interface

1. Ajout de la cinquième région `normandie` dans les couches 2026 sélectionnables par la carte, le menu « Zoom sur », les recherches COG et l'URL directe `?zoom=normandie&niveau=commune&annee=2026&code=50129&zone=normandie`.
2. `docs/assets/lieux-normandie-pactols.js` valide les **deux schémas JSON des registres** : millésime 2026, SHA-256 RDF Pactols, cardinalités 9+7, statut non rétroactif, absence de géométries anciennes, 2 644 codes COG actuels, non-duplication des ARK anciens et réserves explicites. Le module fabrique un index de **16 entrées Pactols**, distinct du COG et du GeoJSON. Les **2 628 autres communes normandes** ont leurs fiches COG et leurs contours 2026, **sans** ARK validé inventé.
3. Les couches COG historiques normandes restent accessibles **depuis 1943** comme états temporels de libellé, codes et mouvements. Pour une année antérieure à 2026, **l'ARK de la commune nouvelle n'est pas présenté comme un alignement validé de cette année**. Si l'option de repère est activée, seul le contour contemporain **2026** peut apparaître, avec mise en forme distincte et avertissement de non-rétroprojection.
4. Les cinq régions métropolitaines désormais couvertes sont PACA, Corse, Pays de la Loire, Bourgogne-Franche-Comté et Normandie. Le zoom national 2026 comporte **9 054 contours** (6 410 auparavant, dont 191 ultramarins, + 2 644 Normandie). La sélection par fenêtre limite les couches métropolitaines demandées à partir du zoom 7. Les quatre ensembles ultramarins demeurent inchangés.
5. Les données COG normandes et les ARK validés se chargent au démarrage du moteur documentaire, comme pour les autres régions ; les **géométries** ne sont récupérées que quand elles deviennent nécessaires. Cette tranche **n'affirme pas** que la consommation de mémoire d'un affichage national de 9 054 contours est optimisée ; le suivi des performances relève de #152.

## Recette bloquante

- Test Node `tests/test_lieux_normandie_pactols.js` sur **les fichiers réellement versionnés** : 2 644 codes géométriques, 16 ARK distincts, quatre exclusions, aucune géométrie déduisant d'elle-même une correspondance Pactols.
- Chromium `tests/test_lieux_normandie_navigateur.py` : lien direct vers Cherbourg-en-Cotentin et son ARK contemporain, lecture de la fiche au millésime **2015** sans réutiliser l'ARK de 2016, recherche directe de l'ARK, fiche de Port-Bail-sur-Mer **sans promotion de Portbail**.
- Chromium `tests/test_lieux_chargement_progressif_navigateur.py` : cache, changement de région, retour national à **9 054 contours**, contrôle de la période de référence et de la recherche.
- Tests statiques des scripts, vérifications générales et non-régressions navigateur PACA, Corse, BFC et PDL ; contrôler les workflows extérieurs impactés avant fusion.
- Pas de nouveau téléchargement de sources officielles ni de modification des géométries dans cette PR : le contenu est celui dont les empreintes ont été vérifiées en #161.

**Point de vigilance :** la présence d'un ARK dans la hiérarchie d'une notice AdlFI ne prouve pas l'identité de la commune à la date de l'opération. Les états COG historiques et la validation documentaire Pactols au millésime 2026 demeurent deux axes distincts.
