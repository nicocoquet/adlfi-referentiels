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


## Résultats du workflow spécialisé

L'exécution [n°44111578059](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44111578059) a réussi, ainsi que la CI générale. Les contrôles de sources par SHA-256 et la reproductibilité bit à bit des rapports JSON sont satisfaits.

La différence `GEO PF Hao 20200 - ISPF Ile 23` totalise **17 398 390,088 m²**, répartis en **654 composantes polygonales** de superficie positive. Les cinq plus grandes représentent **37,14435938 %** de la surface cumulée.

| Rang | Surface m² | Point intérieur (lon, lat) | Emprise (ouest, sud, est, nord) | Trous |
| --- | ---: | --- | --- | ---: |
| 1 | 2 415 216,230 | −140,7412651 ; −18,3624007 | −140,8274977 ; −18,4305186 ; −140,6631417 ; −18,2942823 | 17 |
| 2 | 1 890 678,303 | −140,7531718 ; −18,4187267 | −140,7645479 ; −18,4260687 ; −140,6970197 ; −18,4113828 | 0 |
| 3 | 1 277 374,555 | −140,8136959 ; −18,3995869 | −140,8226452 ; −18,4093028 ; −140,7857683 ; −18,3898717 | 1 |
| 4 | 474 780,394 | −140,8287866 ; −18,2859358 | −140,8334744 ; −18,2946106 ; −140,8248148 ; −18,2772651 | 3 |
| 5 | 404 471,058 | −140,9301156 ; −18,2668435 | −140,9350700 ; −18,2725154 ; −140,9225494 ; −18,2611468 | 4 |

**Attention à la topologie** : le polygone de rang 1 compte **17 anneaux intérieurs** ; son enveloppe géographique couvre une plage assez étendue. Ni sa surface ni son point intérieur ne doivent être interprétés comme une « île » homogène ou comme un lagon. Ces anneaux peuvent influer considérablement sur la signification du polygone.

Les 649 autres composantes représentent environ **10,936 km²** de différence. Pour qualifier la nature géographique, il faudra mettre en regard les cinq premiers polygones avec une orthophotographie/production topographique géoréférencée, documentée par date, résolution et origine. Les noms et types sont pour l'instant **NON_QUALIFIES** ; aucune attribution toponymique automatique ne doit être introduite.

La précision des coordonnées (sept décimales après arrondissement) résulte du format de rapport, **pas** d'une précision métrique garantie. Les données de la PR 87 sont un outil de localisation et de sélection des objets à examiner, non un certificat de délimitation administrative.


## Sources institutionnelles à mobiliser pour qualifier les cinq surfaces

Une vérification documentaire complémentaire identifie deux ressources officielles de la **Direction des affaires foncières** :

1. [Cellule Topographie — Nos services](https://www.service-public.pf/daf/cellule-topo_nosservices/) : les cartes raster produites par la cellule sont géoréférencées en RGPF ; le service distingue les orthophotographies, les cartes récentes, les cartes historiques et les vues satellitaires. La page précise que les vecteurs de la **BD Carto** sont construits à partir de restitutions stéréoscopiques ou aériennes, avec des attributs complétés par des campagnes de terrain ; leur mise à jour moyenne peut se compter en années. Elle rappelle également que les spatio-cartes satellitaires peuvent être soumises à des restrictions contractuelles.
2. [Cellule Topographie — Accueil](https://www.service-public.pf/daf/cadastre/cellule-topo_accueil/) : le géoportail **Te Fenua** permet la superposition d'imageries satellitaires et de cartes topographiques ; la Direction des affaires foncières distingue les données ouvertes, notamment certains rasters et mosaïques aériennes, des images satellitaires soumises à licence restrictive.

Ces sources **attestent la disponibilité générale de fonds géographiques adaptés au contrôle**, et non l'existence d'une scène précisément datée, géoréférencée et librement diffusable sur Hao. Aucun millésime ou résolution de scène n'est donc attribué aux cinq composantes. Avant de les qualifier, rechercher un raster dont l'emprise recoupe leurs boîtes englobantes et relever : **producteur, date d'acquisition, résolution, système géodésique, droit de consultation et de reproduction**. Une consultation du portail n'autorise pas à republier ses images.

Le fait que GEO PF porte `mode_acq=PVS` pour Hao prouve uniquement la valeur déclarée de ce champ, pas que la couche comparée aurait été dérivée de l'image consultée ensuite.
