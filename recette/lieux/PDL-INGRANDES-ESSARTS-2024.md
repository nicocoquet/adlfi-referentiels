# Pays de la Loire — Ingrandes et Essarts : deux mouvements de 2024 non équivalents

**Recette non validante, 18 novembre 2026. Couverture inchangée : 1 215/1 228, 13 exceptions.**

La [recette des neuf collisions Pactols](PDL-NEUF-COLLISIONS-HISTORIQUES-2026.md) et l'instruction des six dossiers restants montrent que les codes INSEE conservés ne garantissent pas une même entité au fil du temps.

## 49160 — Ingrandes-le-Fresne-sur-Loire

- Le **1er janvier 2016**, première commune nouvelle Ingrandes-Le Fresne sur Loire, réunissant Ingrandes et Le Fresne-sur-Loire.
- Le **1er janvier 2024**, nouvelle création par **MOD32**, réunissant cette commune et Saint-Sigismond ; nouvelle dénomination `Ingrandes-le-Fresne-sur-Loire`. [Insee, dossier communal 2026](https://www.insee.fr/fr/statistiques/2011101?geo=COM-49160) ; [arrêté de création du 16 novembre 2023, JORF](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000048728239).
- Le concept Pactols `26678/pcrtQBSwT6fBDW` porte l'intitulé de la **première** commune nouvelle. Le candidat au libellé actuel `26678/pcrtj64zr6gnns4mnfd2828b` existe dans le snapshot RDF, mais n'y possède pas d'`exactMatch` INSEE direct.
- En conséquence, l'ARK de 2016 ne doit pas être attribué à la commune de 2024. Le concept actuel pourra être instruit avec d'autres identifiants et une provenance temporelle contrôlée.

## 85084 — Essarts-en-Bocage

- Création d'Essarts en Bocage le **1er janvier 2016** par réunion de Boulogne, Les Essarts, L'Oie et Sainte-Florence.
- Le **1er janvier 2024**, le COG enregistre le **MOD21** par lequel **L'Oie (85165) et Sainte-Florence (85212) redeviennent des communes** ; la commune restante devient `Essarts-en-Bocage` (trait d'union). La réduction de territoire rend insuffisante l'hypothèse d'un simple renommage. [Insee, dossier communal 2026](https://www.insee.fr/fr/statistiques/2011101?geo=COM-85084) ; [fiche géographique Insee 85084](https://www.insee.fr/fr/metadonnees/geographie/commune/85084-essarts-en-bocage).
- Pactols associe `26678/pcrt0PrU3oVWxo` à « Essarts-en-Bocage » et conserve un concept historique séparé `26678/pcrtFmygG5m3QZ` (Les Essarts).
- Il faut vérifier **la portée du concept Pactols après la scission** avant d'affirmer sa correspondance au périmètre 2026 ; son libellé 2024, un code conservé ou une note historique antérieure ne suffisent pas isolément.

## Objectif du contrôle RDF

`scripts/auditer_pdl_ingrandes_essarts_2024.py` extrait pour chaque concept exact et candidat lexical : `prefLabel`, `altLabel`, `exactMatch` INSEE et Wikidata, autres relations, définitions, notes de portée et d'histoire, tout en vérifiant les épisodes et événements COG.

Le rapport est généré **deux fois** depuis le RDF th17 (Frantiq, 22 juillet 2026, SHA-256 épinglé) et le dérivé COG PDL déjà versionné : aucune prétention de téléchargement actuel des CSV INSEE. Aucune décision, aucune géométrie ou relation historique inférée dans cette PR.

Les autres quatre collisions sont Baugé-en-Anjou, Le Lion-d'Angers, Montsûrs et Le Lude. Les cinq communes sans concept actuel, Les Hauts-d'Anjou et Rives-du-Fougerais restent en instruction. L'interface graphique du module Lieux sera reprise après la consolidation PDL, selon les besoins de l'éditeur.

## Résultats du contrôle RDF th17

[Workflow spécialisé #44365969841](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44365969841) : **réussi**. Les deux rapports générés sont identiques, les 1 215 identités déjà publiées demeurent uniques.

**Ingrandes :** le candidat `26678/pcrtj64zr6gnns4mnfd2828b` possède un `skos:exactMatch` vers `http://id.insee.fr/geo/commune/2cdbc96f-9287-4279-80c9-b3c169bb1fed` — **URI INSEE UUID, précédemment masquée par un parseur limité aux codes numériques** — et vers `https://www.wikidata.org/wiki/Q123475717`. Son `prefLabel` et sa définition visent expressément la commune créée en 2024 ; une note historique indique la création du concept par Inist le 31 mai 2024. Le concept `26678/pcrtQBSwT6fBDW` est limité à la commune de 2016 et son texte indique qu'elle fusionne en 2024. La [fiche Wikidata Q123475717](https://www.wikidata.org/wiki/Q123475717) mentionne `P374=49160` et la création au 1er janvier 2024, mais une éventuelle publication doit figer les déclarations et une révision Wikidata avant de s'en servir comme preuve reproductible. **L'UUID n'est pas considéré comme résolu tant que son identité propre n'a pas été vérifiée.**

**Essarts :** le candidat `26678/pcrt0PrU3oVWxo` possède directement `skos:exactMatch` vers `http://id.insee.fr/geo/commune/85084` ; sa définition fait explicitement état des deux arrêtés préfectoraux de 2023 qui rétablissent les communes de L'Oie et de Sainte-Florence le 1er janvier 2024, et son `prefLabel` reproduit la graphie officielle **Essarts-en-Bocage**. Une note RDF de mise à jour Inist du 3 juin 2024 documente le changement de libellé, de définition et d'alignement. Le concept `26678/pcrtFmygG5m3QZ` vise distinctement l'ancienne commune Les Essarts (avant 2016). Une publication 2026 devient admissible après contrôle spécifique de la portée temporelle, sans confondre le MOD21 de 2024 avec le MOD32 de 2016.

**Bilan :** deux candidats particulièrement favorables, mais la présente recette reste **non validante** : 1 215/1 228 publiés, 13 exceptions. Les preuves administratives, RDF et ontologiques sont maintenant prêtes pour une PR de publication indépendante et contrôlée.
