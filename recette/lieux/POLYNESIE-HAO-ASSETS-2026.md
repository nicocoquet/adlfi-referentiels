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
