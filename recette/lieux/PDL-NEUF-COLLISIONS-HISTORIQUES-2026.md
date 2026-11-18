# Pays de la Loire — neuf collisions historiques Pactols–COG à arbitrer

**Recette documentaire non validante — 18 novembre 2026.** La [publication du lot Wikidata P374, PR 144](https://github.com/nicocoquet/adlfi-referentiels/pull/144), porte à **1 212 / 1 228** la couverture communale contemporaine des Pays de la Loire. Les **neuf communes ayant plusieurs ARK pour un code COG 2026** forment un lot historique distinct des cinq autorités contemporaines non identifiées, des Hauts-d'Anjou et de Rives-du-Fougerais.

## Pourquoi le seul code ne suffit pas

Le COG peut conserver un code lors de la création d'une commune nouvelle, enregistrer plusieurs créations ou expansions successives, ou réutiliser le **même nom** pour un territoire dont les limites ont changé. Un `skos:exactMatch` Pactols vers l'URI `id.insee.fr/geo/commune/{code}` est un indice explicite, mais **ne désambiguïse pas la période de validité du concept** lorsque plusieurs ARK partagent le code.

| Code COG 2026 | Commune | Situation vérifiée dans les épisodes COG versionnés |
|---|---|---|
| `49018` | Baugé-en-Anjou | Création en 2013, élargissement territorial en 2016 ; libellé et code conservés |
| `49160` | Ingrandes-le-Fresne-sur-Loire | Création en 2016, modification en 2024 ; changements graphiques de libellé |
| `49176` | Le Lion-d'Angers | Fusion/commune nouvelle en 2016, même nom et même code |
| `49244` | Mauges-sur-Loire | Création en 2015 à partir notamment de La Pommeraye |
| `53161` | Montsûrs | Ancienne commune, Montsûrs-Saint-Céneré en 2017, nouvelle commune nommée Montsûrs en 2019 |
| `53255` | Sainte-Suzanne-et-Chammes | Création en 2016 à partir notamment de Sainte-Suzanne |
| `72137` | Villeneuve-en-Perseigne | Création en 2015 à partir de La Fresnaye-sur-Chédouet et d'autres communes |
| `72176` | Le Lude | Fusion/commune nouvelle en 2018, même nom et même code |
| `85084` | Essarts-en-Bocage | Création en 2016, évolution en 2024 et changement graphique du nom |

## Chaîne de preuve et limites

Le script `scripts/auditer_pdl_neuf_collisions_historiques_2026.py` examine :
- les **neuf codes**, leurs épisodes `COM` et mouvements `MOD32` dans `docs/data/lieux-chronologie/cog-pdl.json` ;
- tous les **concepts Pactols RDF ayant un `exactMatch` vers le code**, sans réduire les résultats à un ARK par code ;
- les candidats au libellé contemporain sans `exactMatch` vers le code, les `prefLabel`/`altLabel`, la dépréciation/remplacement, les `exactMatch` vers des tiers, les notes d'histoire et de portée, et les autres propriétés utiles ;
- l'absence de promotion d'un ARK déjà utilisé parmi les **1 212 correspondances** publiées.

RDF : `Pactols_Lieux_th17_20260722.rdf`, snapshot Frantiq du 22 juillet 2026 épinglé au commit `69bf9697e24cefd645a69465bbd271702786285a`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`. COG : dérivé PDL 2026 déjà versionné et contrôlé dans les travaux précédents, **sans nouveau téléchargement de l'Insee**.

La recette établit un **diagnostic administratif** distinct de l'arbitrage des concepts. Aucun lien, aucune relation historique ni aucune géométrie n'est ajouté au public. Les résultats JSON et les journaux sont conservés en artefact de CI avec une double génération reproductible.

## Prochain arbitrage

En présence d'un ARK portant le nom de la commune 2026, sa portée temporelle doit encore être prouvée, notamment pour Baugé-en-Anjou, Montsûrs, Le Lion-d'Angers et Le Lude. Pour Ingrandes-le-Fresne-sur-Loire et Essarts-en-Bocage, il faut distinguer nouvelle fusion, rétablissement de communes, et évolution typographique. Une relation conceptuelle ne sera pas inférée des seuls événements administratifs.

Selon les résultats de la recette, des dossiers homogènes pourront passer à une PR de publication **séparée**, avec un registre de preuve par code. Les non résolus seront documentés comme tels. Le chantier d'interface graphique du module Lieux est programmé **après la consolidation PDL** et reprendra les idées éditoriales de l'utilisateur.

## Résultats réels du premier audit

La [recette spécialisée n°44361436698](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44361436698) et les [vérifications générales n°44361436393](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44361436393) sont réussies. Le rapport RDF/COG a reproduit les neuf dossiers sans créer de validation ni géométrie. Les **quatre groupes diagnostiques** ont effectivement pour effectifs **1 + 3 + 2 + 3**.

### ARK contemporains plausibles, mais non encore validés

| COG | Concept Pactols portant le libellé contemporain | Autre concept Pactols, à ne pas promouvoir | Prudence |
|---|---|---|---|
| `49018` | `26678/crtw3s8jkTOZ8` (« Baugé-en-Anjou ») | `26678/pcrthdy1gGxlIV` (« Baugé ») | Notes RDF Insee couvrant la création 2013 et l'extension 2016, mais pas deux ARK de commune nouvelle |
| `49160` | `26678/pcrtQBSwT6fBDW` (« Ingrandes-Le Fresne sur Loire ») | `26678/pcrtD9YKBK1v7E` (Ingrandes ancienne) | Nouveau libellé de 2024 ; le RDF contient aussi un candidat « Ingrandes-le-Fresne-sur-Loire » sans URI INSEE, `26678/pcrtj64zr6gnns4mnfd2828b` |
| `49176` | `26678/pcrtvw6pKPzKU5` (« Le Lion-d'Angers ») | `26678/pcrtQbWytxEJuA` (ancienne commune) | Le concept au nom courant porte aussi une référence externe à l'ancienne commune ; confronter précisément les QID avant validation |
| `49244` | `26678/pcrtVBIl6UNl1S` (« Mauges-sur-Loire ») | `26678/pcrtE0bVL7JsdM` (La Pommeraye) | Notes Insee explicites sur la création du 15 décembre 2015 et les communes déléguées |
| `53161` | **Aucun candidat contemporain qualifié à ce stade** | `26678/pcrt2VftxEe5uH` (« Montsûrs » ancienne), `26678/pcrtzZXdqdUiXm` (« Montsûrs-Saint-Céneré ») | Le même libellé « Montsûrs » est réutilisé pour la commune créée en **2019** : faux positif majeur si l'on retient l'ARK ancien |
| `53255` | `26678/pcrtwUykeFf31u` (« Sainte-Suzanne-et-Chammes ») | `26678/pcrts0lDLWcVyJ` (Sainte-Suzanne ancienne) | Note RDF Insee sur la création du 1er janvier 2016 |
| `72137` | `26678/pcrtoVf9Ovfyy7` (« Villeneuve-en-Perseigne ») | `26678/pcrtg6rwdnGM9r` (La Fresnaye-sur-Chédouet ancienne) | Note RDF Insee sur la création du 1er janvier 2015 |
| `72176` | **À confirmer :** `26678/pcrtoDBez7CbKu` (« Le Lude (Sarthe) ») | `26678/pcrtJ2xcJZw8IO` (« Le Lude (commune déléguée) ») | Nom identique avant et après création 2018, catégories RDF et QID distincts ; ne pas confondre |
| `85084` | `26678/pcrt0PrU3oVWxo` (« Essarts-en-Bocage ») | `26678/pcrtFmygG5m3QZ` (« Les Essarts ») | Notes RDF d'une mise à jour Inist de juin 2024 ; besoin de vérifier le statut administratif après l'évolution de 2024 |

**Orientation :** les trois dossiers Mauges-sur-Loire, Sainte-Suzanne-et-Chammes et Villeneuve-en-Perseigne constituent un premier lot très homogène avec ARK contemporains distincts, `exactMatch` INSEE direct et notes administratives Pactols explicitement datées. Ils sont éligibles **à une recette de publication approfondie**, mais pas publiés par le présent audit. Baugé et Essarts nécessitent une qualification de leurs événements successifs ; Le Lion-d'Angers et Le Lude exigent une désambiguïsation ontologique des concepts ; Ingrandes et Montsûrs demandent une analyse historique renforcée.
