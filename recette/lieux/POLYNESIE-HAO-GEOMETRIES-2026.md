# Polynésie française — Hao : comparer l'unité géographique, l'unité fine et l'île

**17 novembre 2026.** Recette non validante suivant les PR 80–85.

## Point de départ

L'archive GEO PF contient le polygone géographique **`code_geogr=20200` (« Hao »)**, rattaché à la commune associée `IDComas=202` et à l'île `IDIle=23`. La PR 85 a établi pour cette pièce une superficie GEO PF d'environ **33,475 km²**, dont **48,03 %** seulement se trouvent dans la géométrie ISPF de l'unité fine `202`. La différence symétrique totale entre l'unité `202` de l'ISPF et les **cinq** pièces GEO PF de la même unité est d'environ **34,85 km²**.

Cette dissymétrie demande un diagnostic plus fin. Les unités fines, les unités géographiques et les îles constituent **trois échelons distincts**, dont les contours ne doivent pas être confondus.

## Sources

Les trois ressources à SHA-256 immuable sont identiques à celles des PR 83–85 : nomenclature ISPF (`d84f9a69f2c64f744ee0719b01c4841953019d45a1fb29b8abb0db2f3f0176e6`), SIG ISPF (`6302ad2a17ec1fd8b51f70f1d8ba1501ee7ca212a9cd53c8df4221faedfe0b62`) et SIG GEO PF (`29230c18487385f84ca480e9b2c921ea389f848663a4a9574e77b9cbbf40db7b`).

## Protocole PR 86

L'audit `scripts/auditer_hao_ispf_geopf.py` confronte précisément :

- **GEO PF `code_geogr=20200`**, l'objet géographique intitulé Hao ;
- **ISPF `Comas.GeoJSON` `IDComas=202`**, l'unité fine Hao contenant plusieurs objets géographiques ;
- **ISPF `Ile.GeoJSON` `IDIle=23`**, le contour de l'île Hao.

Tous les identifiants et leurs clés de rattachement sont vérifiés dans la nomenclature avant l'analyse. Les trois géométries doivent être individuellement valides et dans le CRS source RGPF EPSG:4687.

Pour chacune, le script mesure les aires sur l'ellipsoïde GRS 1980, le nombre de composantes polygonales, le nombre d'anneaux intérieurs, la surface totale des enveloppes extérieures et celle des trous des polygones. Les trous **ne sont pas assimilés automatiquement** à des lagons : il faudra une interprétation géographique.

Trois comparaisons géométriques sont rapportées : GEO PF 20200 / ISPF Comas 202 ; GEO PF 20200 / ISPF Ile 23 ; ISPF Ile 23 / ISPF Comas 202. Les surfaces non communes sont réparties de part et d'autre, et les **cinq plus grands polygones** de chaque différence sont mesurés, sans exposer leurs coordonnées ou leur géométrie.

Le contrôle de provenance ne démontre ni la date du levé, ni la précision géographique, ni l'indépendance entre ISPF et GEO PF. Les résultats restent un **rapport de recette hors `docs/`** et n'entraînent aucune modification du site ou des autorités.

## Critères de clôture

Fusion uniquement après passage des CI spécialisées et générales et consignation des valeurs effectivement obtenues. Une étape ultérieure pourra rapprocher les lacunes de fonds d'imagerie institutionnels documentés, si nécessaire, sans remplacer les références administratives sans validation.


## Résultats effectifs — comparaison insulaire et non-régression géodésique

Le workflow [n°44109560143](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44109560143) est **réussi**. Il compare exactement les trois contours décrits plus haut, puis réexécute les recettes antérieures après correction de l'orientation des anneaux. Les workflows de vérification générale, des recouvrements PR 82 et des différences de contour PR 84 ont également réussi au même commit.

### Surface et structure des géométries

| Couche | Surface géodésique | Composantes polygonales | Anneaux intérieurs | Aire des trous |
| --- | ---: | ---: | ---: | ---: |
| GEO PF `code_geogr=20200` | **33,475200 km²** | 318 | 0 | 0 |
| ISPF `Ile IDIle=23` | **16,120450 km²** | 228 | 0 | 0 |
| ISPF `Comas IDComas=202` | **44,302622 km²** | 238 | 2 | **27,988986 km²** |

Les deux trous de `Comas 202` concernent l'unité fine **entière**, qui comprend plusieurs objets géographiques et îles ; leur surface ne doit pas être attribuée à Hao sans localisation plus précise. De même, le nombre de polygones n'est pas un nombre d'îles administratives.

### Comparaisons géométriques ciblées

| Paire comparée | Première source hors seconde | Seconde source hors première | Aire commune |
| --- | ---: | ---: | ---: |
| GEO PF Hao 20200 / ISPF île 23 | **17,398390 km²** | **0,043640 km²** | 16,076810 km² |
| GEO PF Hao 20200 / ISPF Comas 202 | **17,395608 km²** | **28,223031 km²** | 16,079592 km² |
| ISPF île 23 / ISPF Comas 202 | **0,000003898 km²** | **28,182177 km²** | 16,120446 km² |

La quasi-inclusion de l'île `23` dans la commune associée ISPF `202` est confirmée : **3,898 m²** de différence extérieure, très faible à l'échelle des contours et à instruire comme tolérance géométrique. GEO PF `20200` couvre **99,73 %** de l'île ISPF `23` mais comporte environ **17,398 km² supplémentaires** hors de son contour. L'emprise longitudinale et latitudinale des deux contours insulaires est très proche (environ 140,66–141,07° O et 18,06–18,43° S), ce qui oriente vers une différence de représentation des éléments récifaux ou littoraux, **sans en fournir la preuve**.

Les cinq plus grandes composantes de GEO PF hors ISPF île 23 ont les aires suivantes (m²) : **2 415 216 ; 1 890 678 ; 1 273 375 ; 474 780 ; 404 471**. Elles ne peuvent être qualifiées de récifs ou de motu précis sans une localisation sur un fond institutionnel.

### Anomalie de calcul corrigée et non-régressions

Le premier test synthétique a montré qu'un calcul ellipsoïdal sur un `Polygon` dont les anneaux ont des orientations non normalisées peut **additionner un trou au lieu de le soustraire**. Deux fonctions partagées ont été corrigées : `aire` dans `scripts/comparer_contours_geopf_ispf.py` et `aire_geodesique` dans `scripts/quantifier_recouvrements_ispf_polynesie.py`, avec `shapely.geometry.polygon.orient(..., sign=1.0)` avant mesure. Les tests de régression couvrent les orientations opposées des anneaux.

Les recalculs sur les archives épinglées confirment **sans changement des valeurs** : le total de la PR 82 (**4 746,027 m²**, 65 paires), les **112 unités** de la PR 84 avec les mêmes quatre exclusions, et les cinq différences symétriques majeures (**35,313 ; 34,851 ; 27,389 ; 22,666 ; 20,654 km²**). La composition des cinq unités de la PR 85 est également inchangée dans le rapport de recalcul.

Cette non-régression concerne **les trois archives épinglées**, non les variantes arbitraires de géométries que les scripts pourront recevoir ultérieurement.

**Statut éditorial :** Hao `20200` reste une comparaison non validante ; aucune correction ni nouveau contour n'est publié. La suite peut qualifier séparément les cinq grandes pièces GEO PF absentes de l'île ISPF sur une image institutionnelle et vérifier les conventions de délimitation.
