# Pays de la Loire — Le Lion-d’Angers et Le Lude : contrôle d'identités homonymes

**18 novembre 2026 — instruction complémentaire non validante.** État public maintenu à **1 217 / 1 228 communes** après PR #148. Ce document complète `PDL-NEUF-COLLISIONS-HISTORIQUES-2026.md` et le suivi #130, sans modifier l'index public.

## Problème

Le **maintien du code INSEE et du nom** lors de créations de communes nouvelles ne garantit pas que l'ARK déjà rattaché à ce code désigne le territoire contemporain. La portée temporelle du concept Pactols reste à justifier de façon indépendante.

## Le Lion-d'Angers — 49176

- **COG** : commune nouvelle créée au **1er janvier 2016**, par réunion d'**Andigné (49005)** et de l'ancienne commune **Le Lion-d'Angers (49176)** ; même nom et même code pour la commune nouvelle.
- **Pactols, audit existant** : candidat au libellé contemporain `26678/pcrtvw6pKPzKU5`; autre concept, ancienne commune `26678/pcrtQbWytxEJuA`.
- **Signal d'alerte externe** : la page DBpedia consacrée à l'**ancienne commune** cite le premier ARK en `rdfs:seeAlso` et associe à sa ressource le QID Wikidata `Q1163281`. Ce rapprochement ne prouve **ni** qu'un `skos:exactMatch` Pactols pointe vers ce QID, **ni** qu'il constitue la meilleure interprétation de l'ARK. Il impose une vérification du RDF Pactols épinglé et des déclarations du QID, **sans promotion automatique**.
- **Sources** : [Insee, commune 49176](https://www.insee.fr/fr/statistiques/2011101?geo=COM-49176), [DBpedia, ancienne commune](https://fr.dbpedia.org/page/Le_Lion-d%27Angers_%28ancienne_commune%29).

**Décision provisoire :** identité contemporaine de l'ARK `pcrtvw6pKPzKU5` **non démontrée** ; maintenir l'exception.

## Le Lude — 72176

- **COG** : commune nouvelle créée au **1er janvier 2018**, par réunion de **Dissé-sous-le-Lude (72117)** et de **Le Lude (72176)** ; même nom et même code.
- **Pactols, audit existant** : candidat au libellé contemporain `26678/pcrtoDBez7CbKu`; concept explicitement délégué `26678/pcrtJ2xcJZw8IO`.
- **Autorité tierce Loterre D63** : la fiche [Le Lude (Sarthe)](https://loterre.istex.fr/D63/fr/page/-JZKZLJCD-0) classe le concept dans **« Nouvelles communes 2018 »** ; elle cite comme concepts spécifiques **Dissé-sous-le-Lude** et **Le Lude (commune déléguée)**, indique le code **72176** et mentionne l'effet au **2018-01-01**. La [fiche distincte « Le Lude (commune déléguée) »](https://loterre.istex.fr/D63/fr/page/-LRKJXJDW-T?clang=en) donne un `exactMatch` explicite vers `26678/pcrtJ2xcJZw8IO` et une URI INSEE de type `communeDeleguee`. Cette distinction **renforce** le diagnostic, mais ne suffit pas à elle seule à certifier l'équivalence exacte entre le **concept Loterre actuel** et l'ARK Pactols `pcrtoDBez7CbKu`.
- **Source administrative** : [Insee, commune 72176](https://www.insee.fr/fr/statistiques/2011101?geo=COM-72176).

**Décision provisoire :** séparation actuelle/déléguée **attestée chez Loterre**, mais identité de l'ARK Pactols contemporain encore **à confirmer par son RDF** ; maintenir l'exception.

## Contrôles reproductibles nécessaires avant publication

1. Réutiliser `scripts/auditer_pdl_neuf_collisions_historiques_2026.py` et le snapshot `Pactols_Lieux_th17_20260722.rdf` (SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`) ; relever **tous** les `skos:exactMatch`, notes, définitions, statuts et remplacements des quatre ARK.
2. Pour chaque QID réellement présent en RDF Pactols, archiver une **révision Wikidata figée** et contrôler `P31`, `P374`, `P571`, statut d'ancienne commune et dates de validité ; ne pas substituer un QID attribué par DBpedia à un `exactMatch` absent du RDF.
3. Confronter ces résultats aux épisodes `COM`/`COMD`, aux mouvements `MOD32` et aux dates du dérivé COG `docs/data/lieux-chronologie/cog-pdl.json`.
4. Ne proposer un ajout au JSON contemporain qu'après décision nominative et tests de régénération, unicité, navigateur et non-régressions.

**Limite de la présente pièce :** consultation de sources externes et des rapports déjà versionnés ; **aucune exécution locale ou CI de l'audit RDF th17** n'est revendiquée. Aucune géométrie, succession ni équivalence ARK–ARK n'est inférée.

**Suite** : Baugé-en-Anjou et Montsûrs, puis bilan des sept autres exceptions. Une fois toutes les décisions explicitées, clôture du lot documentaire PDL et ouverture du chantier distinct d'interface web d'exposition/navigation du référentiel Lieux.
