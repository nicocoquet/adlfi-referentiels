# Raccordement des arrondissements avec le référentiel Lieux PACA

## Sources effectivement comparées

Le module Lieux expose actuellement **103 communes validées en PACA** dans
`docs/data/lieux-communes.geojson`. Leur géométrie provient du fichier
`cartographie/geometries/communes-1000m.geojson` (106 communes) du dépôt
`nicocoquet/atlas-documentaire`, commit
`bc0455c7d1dbf65f579e9b25a01eb7928a8054d5`,
blob Git `0525607f277ec4c915a3e3273e716a5b1f1108d5`.

La géométrie de **Marseille (13055)** existe dans le fichier de 106 communes
mais n'est pas publiée parmi les 103 : son **alignement éditorial Pactols–COG**
était encore à instruire. Sa géométrie source est conservée comme témoin en
`docs/lieux/references/marseille-13055-source-paca-2026.geojson`.

Le lot d'arrondissements est dans
`docs/data/lieux-arrondissements.geojson` (45 arrondissements,
jeu 2026 indiqué « 100 m »), et son union par ville dans
`docs/data/lieux-communes-plm-reconstituees.geojson`.

## Résultats mesurés pour Marseille

Comparaison des ensembles de segments non orientés des anneaux de chaque
géométrie, après normalisation des coordonnées à **quatre décimales**, afin
d'éliminer le bruit flottant introduit lors de l'union des polygones.

| Contrôle | Résultat |
| --- | --- |
| Contour de Marseille dans la source PACA (106 communes) | 7 anneaux, 318 segments |
| Contour dérivé des 16 arrondissements | 7 anneaux, 318 segments |
| Segments communs | **318/318** |
| Segments propres à la source seulement | **0** |
| Segments propres à l'union seulement | **0** |
| Bordure partagée avec Aubagne (13005) du pilote | **18 segments identiques** |
| Bordure partagée avec Allauch (13002) du pilote | **13 segments identiques** |

**Conclusion :** aucune divergence n'est détectée sur la limite extérieure de
Marseille entre la géométrie source du pilote Lieux et les 16 arrondissements
reconstitués. Les segments communs avec Aubagne et Allauch coïncident avec les
contours actuellement exposés sur le module Lieux.

Cette comparaison ne vaut que pour la **géométrie 2026 et pour Marseille**.
Le nom du fichier source PACA indique « 1000 m », tandis que la source des
arrondissements est documentée « 100 m ». Malgré la coïncidence observée,
**ne pas inférer une équivalence générale de ces deux niveaux de généralisation**
pour toutes les communes, ni une validation de leurs limites historiques.
La précision de comparaison (quatre décimales) doit aussi rester indiquée.

## Paris et Lyon : périmètre non comparable au pilote actuel

Les codes **75056 (Paris)** et **69123 (Lyon)** n'appartiennent pas au
périmètre PACA et sont absents du GeoJSON des 103 communes ; le fichier
source de 106 communes ne les contient pas non plus.

La concordance de leurs unions d'arrondissements avec les limites
communales 2026 **reste à contrôler avec des contours communaux nationaux
de même millésime, dont la provenance sera explicitée**. Il ne serait
pas rigoureux d'annoncer une vérification contre le site Lieux actuel
pour ces deux villes.

## Règle d'intégration cartographique

- Lorsque la fiche d'une commune et ses arrondissements sont tous deux
  présents, dessiner **une seule limite communale de référence** et les
  séparations internes des arrondissements ; ne pas superposer deux contours
  concurrents susceptibles de créer de faux décalages visibles.
- Conserver des couches et des identifiants distincts :
  autorité Pactols de la commune, code COG de la commune et codes ARM.
- La concordance géométrique de Marseille ne lève **pas** l'exclusion
  éditoriale antérieure de Marseille du pilote Pactols–COG validé.
- Les limites 2026 ne constituent pas des restitutions historiques.

## Vérification reproductible

Le fichier témoin et `tests/test_lieux_raccordement_paca.py`
assurent le contrôle automatique des 318 segments et des deux raccordements.
Exécution :

```bash
python3 -m unittest discover -s tests -p 'test_lieux_raccordement_paca.py' -v
```

Il reste à effectuer le contrôle externe Paris/Lyon et, pour l'ensemble,
une comparaison plus fine à une référence nationale IGN/COG si
la précision cartographique attendue exige mieux qu'une généralisation 2026.
