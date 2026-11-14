# Lieux — Recette topologique 133 communes et épisodes COG (14 novembre 2026)

**État : vérification technique reproductible et non validante ; PR 24 en brouillon.**

## 1. Références et périmètre

- Source nationale **Contours administratifs 2026, généralisation annoncée à 100 m** :
  `https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2026/geojson/communes-100m.geojson.gz`.
- Empreinte SHA-256 exacte du fichier compressé : `4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778`.
- Jeu de recette : **103 correspondances PACA déjà validées + 30 candidatures nationales non validées**, sans collision ARK/code COG.
- Référence historique d'interface : `docs/data/lieux-communes.geojson` (103 géométries dérivées de `atlas-documentaire/cartographie/geometries/communes-1000m.geojson`).
- Projections pour les mesures : **WGS 84 / EPSG:4326 → Lambert-93 / EPSG:2154** ; Shapely et pyproj.
- Licence de la source cartographique : **ODbL**, avec attribution à Contours administratifs — data.gouv.fr / IGN et contributeurs OpenStreetMap.

Le jeu source complet, qui inclut les communes voisines absentes du pilote, sert d'**enveloppe de comparaison** pour les 133 polygones sélectionnés. Il ne s'agit pas d'une seconde source officielle indépendante (puisque les 133 contours proviennent de cette même source).

## 2. Contrôles topologiques exécutés sur GitHub Actions

Exécution réussie :
https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43592472861

Résultat de l'audit sur la totalité de la source 2026 :

| Contrôle | Résultat |
| --- | ---: |
| Contours sélectionnés | **133** |
| Polygones invalides | **0** |
| Erreurs d'intersection | **0** |
| Polygones sélectionnés ne correspondant pas exactement au polygone source | **0** |
| Recouvrements surfaciques avec un voisin supérieur à 1 m² | **0** |
| Paires de communes contiguës dans les 133 (frontière commune mesurable) | **63** |
| Relations de voisinage constatées avec la source entière | **893 incidences** |
| Contours du pilote PACA comparables | **103** |

Les **893 incidences** ne sont pas 893 paires distinctes : une même paire de communes appartenant toutes deux aux 133 peut être comptée deux fois, une fois depuis chacune des communes. Il s'agit du total des voisins observés pour les 133 objets sélectionnés.

Pour chaque contour, le rapport technique conserve le code, l'intitulé, la validité, la surface, le nombre de composantes, le nombre de voisins et les recouvrements éventuels. L'artefact GitHub contient `rapport-topologie-133.json` et `details-topologie-133.json`.

**Limites du contrôle :**
- l'absence de recouvrement surfacique significatif est vérifiée, mais **l'absence absolue de lacunes (gaps) ne se déduit pas d'une absence de recouvrement** ; elle requerrait une enveloppe indépendante de qualité comparable ;
- une continuité de frontières sur une représentation généralisée ne certifie pas une limite juridique à l'échelle cadastrale ;
- aucune géométrie contemporaine n'est attribuée à une ancienne commune.

## 3. Résultat confirmé : identité géométrique des 103 communes PACA

La différence symétrique **non arrondie**, l'équivalence topologique
Shapely et la distance de Hausdorff ont été calculées entre chaque
contour PACA de `docs/data/lieux-communes.geojson` et le contour 2026
de même code dans la source nationale.

**Résultat : 103/103 équivalents topologiquement, différence symétrique
maximale 0 m², distance de Hausdorff maximale 0 m.**

Ce contrôle plus précis a réussi dans GitHub Actions :
https://github.com/nicocoquet/adlfi-referentiels/actions/runs/43592879414

**Conséquence pour l'intégration :** les 103 contours actuels du
pilote sont déjà compatibles avec la source nationale 2026 à 100 m.
Aucun remplacement de leurs géométries n'est nécessaire.

**Point documentaire restant :** le fichier amont de l'atlas s'appelle
`communes-1000m.geojson`. Sa dénomination semble contradictoire
avec les propriétés de ses 103 géométries exploitées, qui coïncident
avec le jeu 100 m. Ce constat **ne prouve pas** quelle opération
cartographique a réellement été appliquée lors de la fabrication de
ce fichier ; il faut conserver l'empreinte et le chemin de provenance
et éclaircir la chaîne de génération plutôt que renommer arbitrairement
le fichier.

## 4. Modèle des épisodes historiques COG (preuve administrative)

Les fichiers `transitions_code_a_verifier.csv` et `evenements_communaux_particuliers.csv` archivés dans `docs/lieux/recette/lot-001-preuves-cog/` donnent :

- **8** changements de code dus au changement de département (`MOD=41`) : chacun attesté par une ligne COG directe ;
- **15** lignes de mouvements sous `MOD=32`, réparties en **3 opérations** de création de communes nouvelles ;
- soit **23 lignes de mouvement, 11 opérations et 33 états administratifs distincts** dans notre périmètre.

Le script `scripts/construire_episodes_cog_lot001.py` produit trois objets séparés :

1. `operations` : événement administratif (`DATE_EFF`, `MOD`, dossier et preuve) ;
2. `etats_administratifs` : état de type `COM`, `COMD` ou `COMA`, avec code, libellé et dates d'entrée/sortie **attestées par les seuls mouvements du lot** ;
3. `arcs_evenements` : liaison entre état avant et état après pour chaque ligne source.

Les identifiants `ETAT-` et `OP-` sont des **identifiants techniques locaux**, non des identifiants publiés par l'Insee. La date d'entrée / sortie observée dans ces mouvements n'est **pas** une borne officielle d'existence de l'entité si le dossier est incomplet.

Dans Aigondigné, `79185` apparaît sous **Mougon**, **Mougon-Thorigné**, **Aigondigné**, comme autant d'états `COM` distincts ; une commune déléguée `COMD` est encore un autre objet de statut. Il n'y a ni réduction de l'histoire à un code stable, ni création d'un nouvel ARK Pactols.

Pièces en recette :
- `docs/lieux/recette/graphe-episodes-cog-lot001.json` (graph partiel, statut non validant) ;
- `docs/lieux/recette/rapport-episodes-cog-lot001.json` (effectifs, origines) ;
- `scripts/construire_episodes_cog_lot001.py` et `tests/test_episodes_cog_lot001.py` ;
- fichier source Insee des mouvements 2026 : https://www.insee.fr/fr/information/8740222.

## 5. Suite avant toute publication

1. Vérifier l'égalité **non arrondie** et la provenance des 103 contours PACA.
2. Étendre les épisodes historiques depuis le **COG exhaustif depuis 1943**, pour obtenir dates de début/fin complètes et statuts COM/COMD/COMA sans inférence.
3. Joindre les géométries contemporaines par la clé correcte du COG 2026, **jamais par libellé seul**.
4. Soumettre les liens Pactols–COG à validation éditoriale explicite ; les 30 candidatures restent **non validées** et aucune relation `skos:exactMatch` n'est produite.

Le site public (données `docs/data/lieux.json`, `docs/data/lieux-communes.geojson`, interface) demeure inchangé.
