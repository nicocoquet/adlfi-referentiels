# ADR — Hiérarchie territoriale datée et navigations géographiques du module Lieux

**AdlFI · 15 novembre 2026 · proposition de recette indépendante de la PR #30.**  
**Statut : architecture proposée, non publiée.**

## Contexte vérifié

La page publique `docs/lieux/chronologie/index.html` couvre quatre régions courantes (PACA, Corse, Pays de la Loire, Bourgogne-Franche-Comté) avec un curseur **1943–2026** et seulement **des polygones COG 2026**. Le script `docs/assets/lieux-chronologie.js` et son cœur `docs/assets/lieux-chronologie-core.js` pilotent uniquement les états **communaux**. Ils regroupent les codes communaux historiques sous les régions **de 2026** sans reconstituer leur appartenance régionale aux dates demandées ; une note sur la page signale cette limite. L'échelon régional historique ne doit pas être exposé comme s'il existait déjà dans ces données.

Le COG Insee 2026 diffuse **les listes contemporaines** des régions, départements, communes et arrondissements municipaux, et des tables historiques de **couples code–libellé de commune** depuis 1943 ; il n'y a pas dans le lot COG 2026 de table unique `v_region_depuis_1943.csv` équivalente à celle des communes. Les millésimes annuels Insee sont disponibles **de 1999 à 2026** ; les pages officielles archivées **2015** et **2016** contiennent chacune une liste des régions et départements. L'API Métadonnées Insee documente les territoires à une date, les englobements et les prédécesseurs/successeurs ; sa portée exacte est à contrôler avant intégration.

**Évolution régionale :** loi n° 2015-29 du 16 janvier 2015, article 1, fusion des régions métropolitaines **au 1er janvier 2016**. Elle reprend explicitement les anciennes limites au **31 décembre 2015** ; les appellations des nouvelles régions furent initialement provisoires et certaines ont changé au cours de 2016 (article 2). Conserver distincts (i) événement de fusion, (ii) nom daté, (iii) composition de départements, (iv) géométrie à un millésime.

**Important :** ne pas attribuer à **1943** des régions administratives contemporaines. Le domaine temporel des régions antérieures à la disponibilité du COG annuel nécessite une recherche historique spécifique : découpage des régions de programme, circonscriptions d'action régionale, établissements publics régionaux, collectivités territoriales régionales et cas ultramarins. Ne pas inférer qu'un même niveau juridique existe depuis 1943 parce que les communes remontent à 1943.

Sources : https://www.insee.fr/fr/information/8740222 ; https://www.insee.fr/fr/information/2560452 ; https://www.insee.fr/fr/information/2560698 ; https://www.insee.fr/fr/information/2114819 ; https://www.insee.fr/fr/information/5230987 ; https://www.legifrance.gouv.fr/eli/loi/2015/1/16/INTX1412841L/jo/article_1 .

## Interface cible — une seule carte, plusieurs paramètres orthogonaux

1. **« Zoom sur »** contrôle uniquement l'emprise et le centre de la vue. Préréglages : France métropolitaine ; Antilles et Guyane ; océan Indien occidental (Mayotte, Réunion) ; TAAF (vue distincte) ; Pacifique sud (Nouvelle-Calédonie, Wallis-et-Futuna, Polynésie) ; Pacifique nord (Clipperton) ; Atlantique nord (Saint-Pierre-et-Miquelon). L'île des Faisans peut être atteinte par la recherche. *Une vue « Toute la France » sur un planisphère n'est pas le défaut pertinent : territoires très disjoints.*
2. **« Échelon territorial »** contrôle le **type d'entité et de polygone**, indépendamment du zoom : « Région », « Département », « Commune », « Arrondissement municipal ». Ajouter **« Collectivité ou territoire »** pour les COMER, TAAF, Clipperton, sans les classer artificiellement parmi les régions ; prévoir ensuite la distinction « subdivisions COMER » pour `DIS`, `CIR`, `CPT`, `CDM`.
3. **« Situation au »** contrôle la date, de préférence la date exacte derrière un curseur « au 1er janvier » ; les événements intrannuels (fusion au 1er janvier 2016, noms officiels courant 2016, Mayotte 2007/2011/2026, créations/épisodes communaux) sont archivés à leurs dates effectives.
4. **Recherche géographique** interroge les noms **courants et anciens** et propose le type, code COG, période documentaire, éventuel ARK Pactols **validé**. Ne pas présumer que tous les concepts Pactols représentent des unités administratives.
5. **Fiche** : libellé officiel **à la date choisie**, code, statut, appartenance supérieure datée, prédécesseurs/successeurs, lien Pactols si homologué, provenance / millésime du contour. Possibilité d'afficher le périmètre courant **en repère actuel** si le contour ancien n'est pas disponible.

**Éviter l'ambiguïté** : « Arrondissement municipal » signifie seulement les divisions infra-communales de Paris, Lyon et Marseille, et **non** les arrondissements départementaux (zones infra-départementales de sous-préfecture). Le COG les différencie `TYPECOM=ARM` (à contrôler en utilisant la nomenclature effectivement fournie).

**Compatibilités non forcées** : en Polynésie française / Nouvelle-Calédonie, les échelons « Région » / « Département » n'existent pas tels quels au COG. Afficher « Non applicable à ce territoire » plutôt que des couches vides trompeuses. Un zonage `COM` du COG COMER ne doit pas être considéré automatiquement comme commune de droit commun.

## Modèle de données proposé (contrat de recette, à éprouver)

L'interface publique ne doit jamais calculer la géographie historique en remplaçant simplement un nom.

- `territoire` : identifiant interne stable, `niveau`, `nature_cog`, `statut_juridique` daté ou référencé, `origine`, `source`.
- `etat_cog` : `territoire_id`, `code_cog`, `libelle`, `date_debut_incluse`, `date_fin_exclue`, `millesime_source`, `precision_historique`. Le même code peut être conservé malgré une modification du territoire.
- `appartenance` : lien **daté** `enfant_id` → `parent_id` + `type_lien`, `debut`, `fin`, `preuve`. **Ne pas calculer** une appartenance 2015 avec la colonne `REG` du COG 2026.
- `evenement` : `date_effet`, `type`, `entites_avant`, `entites_apres`, `source_juridique` et `source_COG`. Une fusion régionale avec plusieurs prédécesseurs n'est **pas** un simple renommage.
- `geometrie` : `entite_id`, `millesime`, `periode_validite_attestee?`, `source_vectorielle`, `licence`, `precision`, `geojson_ref`, `statut` (historique démontré / contour actuel de comparaison / absent). **Millésime du fichier ≠ période historique démontrée**.
- `alignement_pactols` : ARK, entité COG typée, **millésime de décision**, décision, preuve, éditeur ; ne pas appliquer transitivement un ARK de commune à un département, à une région ou à des états historiques.

Clés de données : `(famille_COG, nature_zonage, code, date)` plutôt que le seul code (homonymie territoriale et réutilisation), et `(entite_id, date)` pour obtenir l'état actif. Utiliser `[debut, fin[` pour toutes les périodes.

### Géométries et distinction de provenance

- **Contours actuels** : jeu **Contours administratifs** utilisé par l'API Découpage administratif, qui propose régions, départements, communes, arrondissements municipaux et divers territoires ultramarins. *Sa couverture et ses sources mixtes doivent être lues explicitement, en particulier pour les COM.*
- **Contours anciens** : la loi 2015-29 décrit les compositions régionales et les limites reprises fin 2015 ; **des données vectorielles datées** sont néanmoins nécessaires pour afficher la situation de 2015. Explorer les archives IGN **GEOFLA** (1997/2002/2010–2016) et **ADMIN EXPRESS** (depuis 2017) comme sources de géométries distinctement millésimées.
- Une **union de polygones contemporains de départements** ne constitue pas un document historique ; si une reconstruction est autorisée, elle doit être affichée comme telle, avec modèle de méthode, date et précision.
- Cartographie monde : gérer les îles disjointes, géométries multipolygones, la longitude ±180° (Pacifique), la généralisation par niveau de zoom, les sources mixtes pour les COM, et le coût des chargements. Ne pas charger la France entière détaillée dès le premier affichage.

Source des limites contemporaines : https://www.data.gouv.fr/datasets/contours-administratifs ; inventaire historique : https://www.data.gouv.fr/pages/donnees-geographiques .

## Ordre de livraison proposé (sans bloquer la PR #30)

| Priorité | Travail | Livrable mesurable |
|---|---|---|
| **P0** | Geler la recette ultramarine `PR #30` : décisions connues Mayotte/Réunion, TAAF clos, autres correspondances en attente ; distinguer validation et préinstruction | PR #30 séparée et cohérente, **sans données de recette dans Pages** |
| **P1** | **Auditer les millésimes régionaux Insee 2015, 2016, 2026**, relations de succession des sept fusions, noms datés, appartenance des départements et statut des DROM/collectivités | CSV/JSON de **recette nationale** + tests et provenance ; pas de géométrie fausse |
| **P2** | Échantillon cartographique **Bourgogne / Franche-Comté → Bourgogne-Franche-Comté** en 2015/2016, contours source 2015 vs 2026, affiliation départementale datée | Prototype indépendant de l'interface actuelle, vérifié éditorialement |
| **P3** | « Zoom sur » + « Échelon territorial » + « Situation au » + recherche multi-échelon, disponibilité progressive des couches | Une page de recette unifiée, accessible, chargement différé par territoire et échelon |
| **P4** | Étendre les autres évolutions régionales, métropole + DROM ; départements historiques et collectivités particulières ; ajouter arrondissements municipaux PLM | Couverture prouvée par millésimes, sans confusion entre départements et collectivités exerçant leurs compétences |
| **P5** | Géométries des COMER et leur typologie spécifique ; Pacifique, Atlantique Nord, TAAF, cas de l'antiméridien | Carte ultramarine complète au millésime disponible ; dates historiques seulement si géométries sourcées |

**Position :** commencer **P1 et un pilote BFC P2 maintenant**, tout en isolant P0 (validation éditoriale ultramarine) dans sa PR d'origine. L'interface serait construite sur ce contrat validé et non l'inverse.

## Premiers contrôles de recette à imposer

1. Pour 2015 et 2016 : **deux listes de régions issues de deux COG distincts**, comparaison par code et par libellé ; anciennes et nouvelles entités distinguées.
2. Sept regroupements métropolitains décrits légalement ; **aucune succession simplement déduite de la ressemblance de noms**.
3. Les régions non fusionnées ont leurs continuités contrôlées individuellement ; ne pas confondre changement de dénomination et évolution des limites.
4. Le département de **2015** ne doit jamais être rattaché par défaut à la région de **2026** dans les états anciens.
5. Aucun `REG` attribué aux COMER qui ne sont pas régions ; les types `COM`, `DIS`, `CIR`, `CPT`, `CDM` restent distincts.
6. L'interface ne doit jamais dessiner un contour 2026 **sans avertissement** pour une année passée.
7. Le champ éditorial des régions AdlFI/BSR (noms historiques) sera **une autorité documentaire distincte** des codes COG datés : les régions BSR ne sont pas des régions 2026 simplement rebaptisées.

