# Arrondissements municipaux — vérification des bordures (COG 2026)

## Méthode

Cette vérification constitue un contrôle **topologique interne**, non une certification
contre une source indépendante de limite communale.

Source : les 45 géométries du fichier `docs/data/lieux-arrondissements.geojson`,
issues des `communes-100m.geojson.gz` de data.gouv.fr (millésime 2026),
licence ODbL. Les surfaces et longueurs sont calculées après reprojection
EPSG:4326 → Lambert-93 EPSG:2154, avec Shapely et PROJ.

Contrôles par ville : validité des polygones et de leur union, recouvrements
d'aire entre arrondissements, nombre de trous, nombre de composantes, mesure
des bordures partagées et conservation du périmètre extérieur après union.
L'invariant de bordure doit être nul :

`Σ(perimeters(arr.)) − 2×Σ(frontières partagées) − perimeter(union) = 0`.

## Résultats du jeu 2026 (généralisation 100 m)

| Commune | ARMs | Union valide | Recouvrements | Trous | Composantes | Bordures internes partagées |
|---|---:|---|---:|---:|---:|---:|
| Paris (75056) | 20 | oui | 0 | 0 | 1 | 67,247 km |
| Lyon (69123) | 9 | oui | 0 | 0 | 1 | 29,896 km |
| Marseille (13055) | 16 | oui | 0 | 0 | 7 | 97,854 km |

Les sept composantes de Marseille correspondent à une grande partie
continentale et six parties séparées au sens topologique. Leur identité
insulaire/littorale exacte doit être confirmée par examen cartographique.

Les surfaces résultantes de l'union sont ~105,438 km² (Paris), ~47,832 km²
(Lyon) et ~237,633 km² (Marseille), selon cette **géométrie généralisée**.
Ce ne sont pas des superficies administratives officiellement certifiées.

## Fichiers produits

- `docs/data/lieux-communes-plm-reconstituees.geojson` : trois contours
  **dérivés par union**, destinés à dessiner une bordure communale sans défaut
  d'alignement avec les arrondissements ; jamais étiquetés « contours communaux
  officiels indépendamment vérifiés ».
- `docs/data/lieux-arrondissements-topologie-2026.json` : rapport quantifié,
  incluant le statut `reference_communale_independante: non_fournie`.
- `scripts/controler_topologie_arrondissements.py` : générateur reproductible,
  pouvant recevoir un GeoJSON de comparaison externe.

## Contrôle indépendant encore nécessaire

Pour certifier que les 45 arrondissements couvrent exactement leurs communes,
il faut fournir les **contours communaux indépendants**, de préférence
issus du produit IGN ADMIN EXPRESS–COG 2026, pour les codes `75056`,
`69123` et `13055`. Le fichier `communes-100m.geojson.gz` contient les
arrondissements et ne constitue pas, à lui seul, un deuxième référentiel indépendant.

Le programme calcule alors :

- la surface du contour communal absente de l'union des arrondissements ;
- la surface de l'union des arrondissements hors contour communal ;
- la différence symétrique et le pourcentage par rapport au contour de référence ;
- la distance de Hausdorff entre les bordures (en mètres).

Ces mesures doivent être interprétées en tenant compte du niveau de
**généralisation** des deux sources ; aucune correction par déformation
ou « snap » automatique n'est effectuée. Le contour de référence, sa date,
son identifiant et son empreinte doivent être conservés pour provenance.

```bash
# Dépendances géospatiales facultatives (hors CI GitHub)
python3 -m pip install 'shapely>=2' pyproj

# Ne modifie ni les sources ni les données publiées par défaut
python3 scripts/controler_topologie_arrondissements.py \
  --communes-reference /chemin/vers/communes-independantes-2026.geojson
```

La page de recette superpose désormais les limites **dérivées** par un trait
plus sombre, au-dessus des contours des arrondissements, sans capter les clics.
