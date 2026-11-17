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
