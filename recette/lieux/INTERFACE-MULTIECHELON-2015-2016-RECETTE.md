# Lieux AdlFI — interface de recette multi-échelon 2015 / 2016

**16 novembre 2026 · PR #31 · prototype autonome hors `docs/`, non publié.**

## Objectif et périmètre réellement couvert

Première recette navigable des trois sélecteurs **« Zoom sur »**, **« Échelon territorial »** et **« Situation administrative au 1er janvier »**. Production d’un **HTML autonome** comportant quatre couches vérifiées :

| Millésime COG | Régions métropolitaines | Départements métropolitains | Édition géographique IGN |
|---|---:|---:|---|
| 2015 | 22 | 96 | GEOFLA DÉPARTEMENT du **04/03/2015** |
| 2016 | 13 | 96 | GEOFLA DÉPARTEMENT du **28/06/2016** |

Soit **227 états administratifs géolocalisés** (35 régionaux + 192 départementaux), sur **deux dates de référence**, et non 227 autorités Pactols.

Le HTML est construit par `scripts/construire_vue_lieux_multiechelon.py` à partir :
- des deux shapefiles GEOFLA originaux contrôlés en EPSG:2154 ;
- des **35 régions déjà reconstruites** à partir des départements de chaque édition ;
- des quatre fichiers officiels COG Insee régions/départements 2015 et 2016, aux empreintes SHA-256 vérifiées.

Les contours sont **simplifiés à 100 m en Lambert-93 uniquement pour l’affichage SVG** et convertis en WGS84 avant inclusion dans le HTML. Les géométries originales et le rapport SIG national restent conservés séparément dans la même exécution CI. Les simplifications individuelles peuvent introduire de petits écarts graphiques aux frontières communes ; ne pas utiliser cette interface pour mesurer des surfaces ou des différences spatiales. Le moteur SVG emploie une projection équirectangulaire adaptée au cadrage métropolitain : ce n'est pas une source métrique.

## Fonctionnement contrôlable

1. **Zoom sur** : France métropolitaine, Bourgogne–Franche-Comté, Pays de la Loire et Corse, avec cadrage indépendant des deux autres paramètres. Les préréglages Antilles–Guyane, océan Indien, Pacifique, Atlantique Nord, TAAF–Clipperton sont **visibles mais non disponibles** ; aucune couche fictive n'est affichée.
2. **Échelon territorial** : régions ou départements. « Commune », « Arrondissement municipal » (Paris, Lyon, Marseille) et « Collectivité ou territoire » signalent explicitement l'absence de données qualifiées **dans ce prototype**, sans substituer de polygones départementaux.
3. **Situation au** : COG au 1er janvier **2015** ou **2016** ; 2026 est présent comme option **indisponible**. Une édition IGN datée de mars/juin n'est jamais présentée comme géométrie juridique certifiée au 1er janvier.
4. **Recherche** : nom ou code, avec propositions distinguant année et échelon. La sélection peut changer explicitement ces deux paramètres si le résultat trouvé appartient à un autre instantané.
5. **Fiche** : code COG et nom à l'instantané, parent régional pour les départements, composition en départements pour les régions, édition géométrique, qualification, références Insee. Aucun ARK Pactols n'est inféré.
6. **Filiations et réserves** : sept fusions du 01/01/2016, maintien des autres codes régionaux, dénomination **Centre** au 01/01/2015 et noms régionaux provisoires au 01/01/2016. Pour les départements **44** et **49**, mention du transfert légal du Fresne-sur-Loire prenant effet le **31/12/2015** et distinct de la création de la commune nouvelle au 01/01/2016.
7. Carte SVG autonome, sélection souris/clavier, boutons zoom +/–, restauration du cadrage, sans chargement d'un script tiers.

## Garde-fous et tests

- Données de recette **interdites sous `docs/`** ; la PR reste un brouillon.
- Vérification des **22 + 13 + 96 + 96** entités, du CRS source, des codes régionaux et des liens département → région datés.
- Empreintes SHA-256 des quatre sources COG ; géométries issues exclusivement des éditions IGN correspondant aux états.
- Simplification géométrique : contrôle des géométries non vides et valides.
- Aucun alignement Pactols, aucune rétroprojection des limites 2026.
- Production deux fois du HTML et du rapport, comparée **octet par octet**.
- Tests unitaires de présence des contrôles, du refus de publication, de la sécurité du JSON embarqué et de la validation des sources.
- Essais navigateur locaux sur Chromium : affichage des régions et départements, recherche datée, changement d'année, interdiction d'afficher 2026 ; sans erreur JavaScript observée.

## Livrables

Dans l'artefact de la CI GEOFLA 2016 :

- `recette/AdlFI_Lieux_Multiechelon_2015_2016.html` : interface autonome de recette.
- `recette/rapport-interface-multiechelon-2015-2016.json` : tailles, SHA-256, cardinalités et restrictions.
- Les données régionales/départementales de contrôle et les archives originales continuent d'être conservées dans l'artefact.

## Étape suivante proposée

Après recette éditoriale de l'ergonomie et du contrat de données :
- intégrer les **communes historiques** déjà préparées, mais uniquement là où l'état COG daté et les géométries peuvent être qualifiés sans rétroprojection ;
- intégrer les **arrondissements municipaux PLM** en distinguant le niveau administratif et les mentions éditoriales non indexées Pactols ;
- qualifier les **couches des DROM** séparément de celles des COMER et des collectivités à statut particulier ;
- n'activer les années antérieures à 2015 que sur sources cartographiques réellement millésimées et les états juridiquement qualifiés.

**Aucune publication ni fusion automatique de la PR #31 ; aucun alignement Pactols nouveau.**
