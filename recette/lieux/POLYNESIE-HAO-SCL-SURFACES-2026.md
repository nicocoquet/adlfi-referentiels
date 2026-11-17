# Hao — Classification SCL sur les cinq principales surfaces de différence (PR 91)

**17 novembre 2026.** Suite aux PR 87–90, recette logicielle non validante.

## Problématique et périmètre

Les cinq plus grandes composantes de `GEO PF code_geogr=20200 - ISPF Ile IDIle=23` totalisent environ **6,463 km²**. La PR 89 permettait d'interroger les pixels de **cinq points intérieurs**. Cette étape ne pouvait pas caractériser l'ensemble de chaque polygone.

La PR 91 prépare une **statistique zonale sur les surfaces complètes** : répartition des classes SCL, pixels masqués, et nombre de centres de pixels inscrits dans les cinq premières composantes. Elle ne constitue **ni une cartographie des récifs ni une validation juridique des contours**.

## Sources et chaîne de provenance

L'analyse attend localement :

- l'archive officielle GEO PF SHP, SHA-256 `29230c18487385f84ca480e9b2c921ea389f848663a4a9574e77b9cbbf40db7b` ;
- l'archive GeoJSON officielle ISPF, SHA-256 `6302ad2a17ec1fd8b51f70f1d8ba1501ee7ca212a9cd53c8df4221faedfe0b62` ;
- `SCL_20m.jp2` de la scène Copernicus `S2A_MSIL2A_20221226T193851_N0510_R056_T07KEV_20240715T211924` ;
- le `manifest-local.json` préparé par la PR 90, qui associe la bande SCL à la date, à l'identité du produit et à son SHA-256.

L'audit s'arrête si le manifeste, l'empreinte du fichier SCL ou l'une des sources institutionnelles ne correspond pas. La géométrie de chaque composante est hachée (WKB) dans le rapport, sans reproduire le polygone.

## Méthode spatiale

La différence vectorielle est effectuée dans les coordonnées RGPF natives (**EPSG:4687**) et classée par surface ellipsoïdale (**GRS 1980**), comme dans les PR 86 et 87. Les cinq premières composantes sont projetées vers le **CRS lu dans le raster JP2** : aucun code EPSG UTM n'est imposé.

Pour chaque polygone, `rasterio` lit uniquement sa fenêtre de pixels nécessaire, puis applique la convention de sélection **centre de pixel à l'intérieur** (`all_touched=False`). Cela évite d'additionner mécaniquement tous les pixels tangents aux limites, mais sous-estime ou surestime éventuellement les petites surfaces et les franges fines. Le nombre de cellules SCL incluses ne constitue **pas une aire géodésique exacte**. Les cellules NoData sont comptabilisées à part. La proportion de chaque classe est calculée uniquement sur les pixels valides.

Les codes SCL officiels distinguent notamment eau, végétation, surfaces non végétalisées, nuages et ombres. Ils reflètent un **algorithme de classification Sentinel-2**, dont la résolution native est **20 m**, et non des catégories géomorphologiques permettant de distinguer avec certitude motu, récif émergé ou récif submergé.

## Procédure locale

Depuis la racine du dépôt après récupération des cinq JP2 selon la PR 90 :

```bash
D="$HOME/Downloads/AdlFI-Hao-Sentinel2-20221226"
python3 scripts/analyser_surfaces_scl_hao.py \
  --geopf "$HOME/Downloads/loc-commune-associee.zip" \
  --ispf-geojson "$HOME/Downloads/ispf-geojson.zip" \
  --scl "$D/SCL_20m.jp2" \
  --manifest "$D/manifest-local.json" \
  --sortie "$D/hao-surfaces-scl.json"
```

**Important :** les noms ci-dessus pour les deux archives SIG sont des **exemples à adapter** à leurs noms de téléchargement réels. Les SHA-256 sont obligatoirement vérifiés avant analyse. Ne commiter **ni les images, ni les rapports de pixels, ni les identifiants Copernicus**.

## Contrôles et suite

La CI ne télécharge **aucune image authentifiée** et ne prétend pas produire des résultats SCL pour Hao. Des GeoTIFF synthétiques vérifient les transformations de coordonnées, les comptages eau/nuage, l'exclusion des NoData et les géométries hors emprise ; un manifeste local fictif vérifie le rejet d'un raster altéré.

Même si les cinq surfaces présentaient majoritairement `SCL=6` (eau) ou `SCL=5` (non végétalisé), la conclusion ne serait **pas** « récif » ou « motu » sans croisement avec la réflectance multispectrale, l'imagerie visible et une source topographique indépendante.

**Statut : `RECETTE_NON_VALIDANTE`. Aucun contour, raster, toponyme ou ARK ajouté au site.**
