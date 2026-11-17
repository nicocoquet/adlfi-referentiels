# Polynésie française — Hao : localisation des cinq grandes composantes hors contour insulaire ISPF

**17 novembre 2026.** Suite à la PR 86. **Recette non validante.**

## Problème géographique

Le diagnostic de la PR 86 a établi que le contour GEO PF `code_geogr=20200` (Hao) comprend **17,398390 km²** situés hors du contour ISPF `Ile IDIle=23`. Le contour GEO PF est presque deux fois plus étendu en surface polygonale ; les deux sources ont néanmoins des emprises géographiques semblables. Cette différence ne peut être assimilée sans preuve à un récif, un lagon ou des îlots spécifiques.

## Méthode de localisation

`scripts/localiser_composantes_hao_geopf.py` reprend exactement les deux archives géométriques institutionnelles, avec les SHA-256 :

- ISPF SIG : `6302ad2a17ec1fd8b51f70f1d8ba1501ee7ca212a9cd53c8df4221faedfe0b62` ;
- GEO PF SIG : `29230c18487385f84ca480e9b2c921ea389f848663a4a9574e77b9cbbf40db7b`.

L'outil calcule la différence spatiale `GEO PF 20200 - ISPF Ile 23` dans les coordonnées natives RGPF EPSG:4687 (sans reprojection), décompose les `Polygon` et `MultiPolygon` et mesure leurs aires sur l'ellipsoïde GRS 1980. Il classe toutes les composantes surfaciques par aire décroissante et fournit pour les cinq premières :

- surface géodésique en m² ;
- emprise géographique `[ouest, sud, est, nord]` en longitude-latitude ;
- un point garanti **à l'intérieur** de la composante, fourni à titre de repère cartographique, sans prétendre qu'il s'agit d'un centroïde ;
- nombre d'anneaux intérieurs, pour ne pas confondre présence d'un trou et absence de matériau terrestre.

L'aire totale des pièces et la part des cinq plus grandes sont documentées. Les géométries exactes ne sont pas recopiées dans le rapport.

## Limites de preuve

Ces coordonnées permettent de localiser un écart **géométrique**. Elles n'identifient pas sa nature (récif, motu, lagon, zone humide, erreur de numérisation). Les deux sources institutionnelles peuvent partager une généalogie cartographique ; le caractère indépendant du fond GEO PF n'est pas démontré. Le premier contrôle ne propose **ni nouveau toponyme ni correction automatique**.

L'étape de qualification des cinq surfaces nécessite une **source indépendante documentée** (orthophotographie, carte topographique ou données spécialisées), dont la date et la résolution soient connues. Une image illustrant l'atoll sans localisation précise n'est pas une preuve suffisante.

## Publication et sécurité éditoriale

La CI produit un JSON reproductible en artefact GitHub Actions, hors `docs/`. Aucune autorité, ARK ou géométrie du module Lieux n'est créée ou modifiée. La PR peut être fusionnée une fois les contrôles réalisés ; elle ne constitue **pas** une homologation des limites insulaires.
