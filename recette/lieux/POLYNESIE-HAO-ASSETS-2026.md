# Polynésie française — Hao : inventaire des assets Sentinel-2 L2A (PR 89)

**17 novembre 2026 — recette non validante, après PR 88.**

## Produit sélectionné

Le contrôle du catalogue Copernicus de la PR 88 a confirmé une acquisition Sentinel-2A L2A datée du **26 décembre 2022, 19:38:51 UTC**, avec une géométrie STAC contenant les cinq points intérieurs calculés dans la PR 87.

- Produit exact : `S2A_MSIL2A_20221226T193851_N0510_R056_T07KEV_20240715T211924`.
- [Fiche du produit dans le catalogue STAC CDSE](https://stac.dataspace.copernicus.eu/v1/collections/sentinel-2-l2a/items/S2A_MSIL2A_20221226T193851_N0510_R056_T07KEV_20240715T211924).
- Nuages : **3,53 %** déclarés pour la tuile entière, pas pour les cinq pièces de l'écart GEO PF–ISPF.
- La date `20240715` dans l'identifiant fait partie du nom du produit traité ; elle ne doit pas être lue comme la date d'acquisition.

## Méthode et vérifications

`scripts/inventorier_assets_hao_sentinel2.py` récupère uniquement l'**item STAC exact** : vérification de l'ID, de la collection et de la date, contrôle géométrique de l'empreinte sur les cinq points PR 87, inventaire des clés d'assets, des types MIME, des rôles, et des informations de projection (`proj:epsg`, `proj:shape`, `proj:transform`) ou de résolution nominale lorsqu'elles sont effectivement renseignées.

Le contrôle n'interprète pas une chaîne « B02 » ou « SCL » comme un fichier exploitable tant qu'un asset réel et son type ne sont pas présents. Il n'imprime pas les URL complètes des assets : seul leur domaine, protocole et suffixe apparaissent dans le rapport, pour ne pas exposer d'éventuels paramètres sensibles.

Le produit Sentinel-2 L2A comprend normalement des bandes de réflectance et une couche de classification de scène (`SCL`). Les bandes visibles **B02, B03, B04** sont natives à 10 m, tandis que la classification SCL utilise une autre résolution spatiale ; il serait donc erroné de comparer les pixels ligne à ligne sans lire les grilles et rééchantillonner de manière justifiée. Le nom d'une collection ou d'un asset ne garantit pas une résolution effective attestée pour cet item.

Sources : [documentation CDSE Sentinel-2](https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel2.html) et [catalogue STAC CDSE](https://documentation.dataspace.copernicus.eu/APIs/STAC.html).

## Limites de preuve et décisions

La présence d'un asset accessible et renseigné ne prouve pas que les pixels dans les cinq polygones sont exempts de nuages, qu'ils distinguent les récifs émergés et immergés, ou qu'ils permettent une délimitation juridique. Aucun raster n'est téléchargé dans cette tranche ; aucun rendu RGB, masque de qualité ou classification radiométrique n'est déclaré accompli.

**Statut `RECETTE_NON_VALIDANTE`**. L'artefact CI contient les métadonnées du produit et l'inventaire effectif de ses assets. **Aucun pixel ni polygone publié** ; aucun nouveau nom, ARK ou autorité ajouté. La décision ultérieure sera prise d'après les URL, formats, CRS, conditions d'accès et possibilités de lecture effective à l'échelle des cinq surfaces.


## Résultats effectifs du préflight et verrou d'accès

Le workflow [n°44115483638](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44115483638) est **réussi**. L'item du 26 décembre 2022 fournit **47 assets**. Ont été identifiés, chacun au format **JPEG 2000** :

| Clef STAC effective | Rôle déclaré | Résolution annoncée dans les rôles |
| --- | --- | --- |
| `B02_10m` | reflectance, original | 10 m |
| `B03_10m` | reflectance, original | 10 m |
| `B04_10m` | reflectance, original | 10 m |
| `B08_10m` | reflectance, original | 10 m |
| `TCI_10m` | visual, original | 10 m |
| `SCL_20m` | classification de scène, original | 20 m |
| `CLD_20m` | information de nuage | 20 m |

Le schéma source ne donne pas de valeur `proj:epsg` dans les assets ci-dessus. Le géoréférencement doit donc être **lu dans les en-têtes JP2 réels** avant toute comparaison de pixels. Les liens des bandes et du masque sont des URI **`s3://eodata/…`** et non des liens HTTP publics directs. Le STAC fournit par ailleurs un asset `Product` (archive ZIP par HTTPS) et une vignette JPEG, mais une vignette non géoréférencée ne fournit pas les données nécessaires à une expertise pixel par pixel.

La [documentation officielle CDSE de l'accès S3](https://documentation.dataspace.copernicus.eu/APIs/S3.html) indique que l'accès à `eodata.dataspace.copernicus.eu` demande la création de **clés S3 liées à un compte Copernicus**. Cette recette ne dispose pas de ces clés et **n'a téléchargé aucun JP2**. Aucun accès aux pixels, absence locale de nuages ou classe littorale n'est donc revendiqué.

## Outil de contrôle des pixels préparé et testé sur données synthétiques

Le script `scripts/diagnostiquer_pixels_hao_l2a.py` accepte en entrée **les cinq fichiers locaux** `B02_10m`, `B03_10m`, `B04_10m`, `B08_10m` et `SCL_20m`. Avec `rasterio`, il lit leur CRS, dimensions, pas de grille et valeurs au niveau des **cinq points intérieurs PR 87**. Une transformation explicite de coordonnées WGS84 vers le CRS du raster est appliquée pour chaque point ; les cellules hors image et no-data sont signalées sans être transformées en valeur nulle fictive. L'interprétation de la couche SCL est limitée à l'étiquette automatique du pixel ; ni ce résultat ni les couleurs visibles ne valident la nature géographique de la surface entière.

La conformité de résolution 10/20 m est vérifiée sur les fichiers, et les fichiers dotés de CRS divergents sont refusés. Les noms et le choix des fichiers en arguments restent la **responsabilité de l'opérateur** : le script ne prouve pas que ceux-ci appartiennent réellement au produit STAC tant qu'un manifeste et leurs empreintes ne sont pas conservés.

Tests intégrés à la CI spécialisée : synthèse GeoTIFF projetée en UTM, vérification du pixel attendu, refus d'une entrée incomplète ; la suite générale n'exige pas les dépendances géographiques.

**Résultat éditorial :** préflight de métadonnées documenté, lecteur de points reproductible prêt à fonctionner **après obtention légitime des fichiers**, sans prétendre disposer des valeurs de pixels pour Hao. Il n'est pas nécessaire de communiquer des clés S3 ou des secrets dans la conversation ou dans une PR. Pour une exécution distante authentifiée, les secrets devront être fournis à un environnement sécurisé et jamais enregistrés dans les fichiers du dépôt ou les journaux CI.
