# Arrondissements municipaux — lot de recette AdlFI (COG 2026)

## Finalité et statut

Lot **distinct** de la table Pactols–COG du pilote PACA et de l'extraction
nationale des autorités Pactols : **45 arrondissements municipaux**, sous
identifiant administratif du COG 2026, et les contours officiels 2026.
Le lot reste **en recette** ; les jeux de données sont déposés sur une branche
spécifique, jamais fusionnés directement dans `main`.

La règle métier est **une autorité géographique indépendamment de son nombre
d'occurrences AdlFI** : 32 arrondissements ont au moins une attestation dans un
titre AdlFI, et 13 autres sont conservés parce qu'ils figurent dans le COG.
Il n'est publié aucun comptage de notices, ni liste des notices d'où provient
l'attestation : ce renseignement relève d'un futur module documentaire/atlas.

## Provenance

- **Identifiants administratifs et relations parentales** : Insee,
  [Code officiel géographique au 1er janvier 2026](https://www.insee.fr/fr/information/8740222),
  fichier `v_commune_2026.csv`, sélection `TYPECOM=ARM`, `COMPARENT`
  égal à `75056`, `69123` ou `13055`. SHA-256 source :
  `7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3`.
- **Géométries** : [Contours administratifs](https://www.data.gouv.fr/datasets/contours-administratifs),
  millésime 2026, fichier `communes-100m.geojson.gz`, généralisation 100 m,
  licence ODbL. SHA-256 du fichier source compressé :
  `4530cbf87a3af387c2da95935376f74b93eabd0a7595eacc5b7e0ed94a0b3778`.
- **Attestations XML AdlFI** : extraction nationale v2 (titres de notices),
  SHA-256 de `notices.csv` :
  `b46a856a53c2556102f61ee0e1761a9e52f1267be92efaf3c0d1284c49feb1b7` ;
  SHA-256 d'`occurrences_lieux.csv` :
  `b2e7332515c051e0c63e1fb29c840fa338aa85040fb2358a7df64d735b2942cd`.

**Nature du lien Pactols** : le champ `commune_parente.ark_pactols`
désigne **uniquement la commune** (Paris, Lyon ou Marseille), attestée par
l'index Pactols des notices correspondant aux mentions de titre.
**Aucun ARK d'arrondissement n'est créé**, et aucune équivalence
`skos:exactMatch` entre Pactols et COG n'est inférée.
Le lien ARK–commune ne remplace pas une validation nationale COG–Pactols
encore en cours.

Les contours de 2026 **ne sont pas des géométries historiques**.
Pour établir des périodes de validité administrative, utiliser les fichiers
historiques du COG (« Communes depuis 1943 » et « événements sur les communes »),
qui ne sont pas intégrés dans ce lot.

## Sources et effectifs

| Sous-ensemble | Total officiel | Attesté dans les titres AdlFI |
| --- | ---: | ---: |
| Paris | 20 | 18 |
| Lyon | 9 | 6 |
| Marseille | 16 | 8 |
| **Total** | **45** | **32** |

Dans la première extraction, **381 mentions de titre** ont été reconnues :
373 simples, cinq mentions multi-arrondissements explicites et trois
mentions à trait d'union soumises à une instruction éditoriale.
Les 378 mentions directes/explicites produisent 383 associations
notice–arrondissement. Les associations ne sont pas exportées dans le
référentiel public.

### Trois mentions à contrôler éditorialement

1. `Lyon (1er-2e) – Place Saint-Nizier, rives de Saône : terrasses de la presqu’île` :
   candidats 69381 et 69382 ; ne pas interpréter comme intervalle.
2. `Lyon (1er-5e) – Anciennes galeries de captage d’eau sous les collines de Fourvière et de la Croix-Rousse` :
   candidats 69381 et 69385 ; ne pas ajouter 2e, 3e ou 4e.
3. `Lyon (4e-9e) – Réalisation du Pont Schuman` :
   candidats 69384 et 69389 ; ne pas ajouter les arrondissements intermédiaires.

Les trois cas ne créent **aucune relation validée** tant que l'éditeur n'a pas
confirmé la signification des deux numéros.

## Fichiers intégrés

- `docs/data/lieux-arrondissements.json` : 45 autorités, codes et parents,
  type `ARM`, statut d'observation booléen, références de provenance.
- `docs/data/lieux-arrondissements.geojson` : 45 géométries du jeu source
  2026 avec codes COG et commune parente.
- `scripts/valider_lieux_arrondissements.py` : contrôle du contrat métier,
  de la complétude et des coordonnées, **sans dépendance externe**.
- `tests/test_lieux_arrondissements.py` : six tests de non-régression.
- `docs/lieux/arrondissements-recette.html` : prévisualisation cartographique
  en recette, séparée du moteur actuel des 103 correspondances PACA ; page
  non liée depuis le site et à vérifier localement.

## Contrôles réalisés sur les données remises

- 45 codes uniques et attendus (`75101`–`75120`, `69381`–`69389`,
  `13201`–`13216`) ; aucune discordance de commune parente ou d'ARK.
- 45 géométries de type `Polygon` (42) ou `MultiPolygon` (3), toutes
  **valides** au sens des règles OGC vérifiées avec Shapely ; aucun anneau vide
  ni géométrie hors zone.
- Reprojection en Lambert-93 (EPSG:2154), contrôle des intersections
  par paires dans chaque commune : **aucun chevauchement de surface**.
- Chaque propriété géométrique correspond aux propriétés de l'autorité
  COG de même code.
- Concordance des 381 mentions documentaires et de leurs ARK de commune.
- Les 6 tests de non-régression de l'exporteur ont réussi localement.

**Limite explicite** : ce contrôle ne confronte pas la réunion des 45
arrondissements à la géométrie des trois communes parentes issue de la
même source ; il ne démontre donc pas l'absence de petites lacunes de
frontière dues à la généralisation. Cette recette complémentaire pourra être
réalisée avec les données complètes de référence sur le Mac de l'éditeur.

## Recette locale

Depuis la racine du dépôt Git :

```bash
python3 scripts/valider_lieux_arrondissements.py
python3 -m unittest discover -s tests -p 'test_lieux_arrondissements.py' -v
node --check docs/assets/lieux-arrondissements-recette.js
python3 -m http.server 8000 -d docs
```

Ouvrir `http://localhost:8000/lieux/arrondissements-recette.html` : vérifier
les 45 contours, la recherche par nom et code COG, la sélection et les liens
ARK de la commune parente, sur ordinateur et mobile.

Le moteur principal du module Lieux (`docs/lieux/index.html`) et ses 103
correspondances PACA ne sont **pas modifiés** par cette recette. La fusion et
l'éventuelle intégration des arrondissements dans l'autocomplétion commune
restent conditionnées à une validation éditoriale et visuelle distincte.