# Polynésie française — composition géographique des cinq écarts GEO PF / ISPF (PR 85)

## Objet de l'instruction

Après la PR 84, cinq unités fines présentent les écarts de contours les plus importants : **`190`, `202`, `112`, `263`, `264`**, dans cet ordre de surface de différence symétrique décroissante (respectivement environ 35,31 ; 34,85 ; 27,39 ; 22,67 ; 20,65 km²).

La première question n'est pas de décider quel tracé est « exact » : il faut établir **la composition des polygones** et les **métadonnées d'acquisition**. L'archive GEO PF de 2022 rassemble 179 entités géographiques alors que le GeoJSON `Comas` ISPF expose 116 unités fines agrégées. Les composantes géographiques possèdent des codes `code_geogr` et des rattachements qui permettent une comparaison documentée.

## Sources et méthode

Sources vérifiées par SHA-256, comme dans les PR 83 et 84 :

- ISPF XLSX : `d84f9a69f2c64f744ee0719b01c4841953019d45a1fb29b8abb0db2f3f0176e6`
- ISPF GeoJSON : `6302ad2a17ec1fd8b51f70f1d8ba1501ee7ca212a9cd53c8df4221faedfe0b62`
- GEO PF SHP : `29230c18487385f84ca480e9b2c921ea389f848663a4a9574e77b9cbbf40db7b`

`scripts/auditer_composition_geopf_top5.py` contrôle `IDGeo/code_geogr`, `IDComas/code_com_1`, `IDCom/code_commu`, `IDSub/code_subdi`, `IDIle/id_ile`. Il refuse les rattachements incohérents et une couverture incomplète de l'unité étudiée.

Pour chacune des cinq unités, le rapport indique : codes et noms des pièces GEO PF, île, mode et organisme d'acquisition, nombre de composantes des géométries, surfaces de GEO PF / ISPF, surfaces respectives extérieures au contour de l'autre source et taux de recouvrement de chaque pièce GEO PF par le contour ISPF.

Les mesures de surface utilisent l'ellipsoïde **GRS 1980**, sans fixer de seuil arbitraire de divergence. L'unité `190` (Gambier) comprend **16 codes géographiques** `19001`–`19016`, dont aucun `19000` : ces pièces doivent être évaluées ensemble avant toute interprétation d'un écart.

## Limites de preuve

Les attributs `mode_acq` / `org_acq` documentent l'acquisition déclarée dans le fichier GEO PF, **pas la précision effective, la date de levé ou l'indépendance géométrique**. La différence entre GEO PF et ISPF peut être due à des conventions de périmètre ou de littoral, à des mises à jour, ou à d'autres causes non démontrées. Les tests ne modifient aucun polygone et n'imputent pas une erreur à l'un des organismes.

Le rapport est produit en artefact CI, hors `docs/`. **Statut : `RECETTE_NON_VALIDANTE`.** La publication cartographique attend l'instruction des écarts et des métadonnées sources.


## Résultats effectifs du 17 novembre 2026

L'exécution initiale [n°44107270782](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44107270782) a réussi (ainsi que la CI générale). Les fichiers de sources sont contrôlés par les trois SHA-256 institutionnels déjà documentés et le rapport est identique après deux calculs indépendants.

### Composition et dissymétrie des différences

| `IDComas` | Pièces `IDGeo` | Composantes polygonales ISPF | Composantes GEO PF (avant agrégation) | ISPF hors GEO PF (km²) | GEO PF hors ISPF (km²) |
| --- | ---: | ---: | ---: | ---: | ---: |
| `190` — Gambier | 16 | 81 | 271 | 34,919 | 0,394 |
| `202` — Hao | 5 | 238 | 409 | 17,424 | 17,427 |
| `112` — Anaa | 3 | 49 | 157 | 27,134 | 0,255 |
| `263` — Raroia et Takume | 2 | 104 | 386 | 22,501 | 0,166 |
| `264` — Taenga et Nihiru | 2 | 24 | 141 | 19,734 | 0,920 |

Ces effectifs de **composantes polygonales** représentent des anneaux extérieurs et îlots dans la géométrie, **pas** de nouvelles autorités ni nécessairement des îles administrativement identifiées. La dissymétrie de quatre unités (`190`, `112`, `263`, `264`) justifie de tester l'hypothèse d'une **convention d'emprise des atolls différente**, y compris éventuellement la représentation de surfaces lagonaires. La seule mesure de différence symétrique ne suffit pas à prouver cette hypothèse. Pour `202`, les surfaces manquantes sont presque égales de part et d'autre, et appellent une analyse spatiale propre.

### Métadonnées d'acquisition effectivement observées

| Unité | Modes déclarés dans les pièces GEO PF | Organismes déclarés |
| --- | --- | --- |
| `190` | 8 `PVS`, 3 `ORTHO`, 5 `AUTRE` | 14 `INTERNE`, 2 `ISPF` |
| `202` | 1 `PVS`, 4 `TERRAIN_TOPO` | 1 `INTERNE`, 4 `CADASTRE` |
| `112` | 3 `TERRAIN_TOPO` | 3 `CADASTRE` |
| `263` | 2 `TERRAIN_TOPO` | 2 `CADASTRE` |
| `264` | 1 `ORTHO`, 1 `TERRAIN_TOPO` | 1 `INTERNE`, 1 `CADASTRE` |

Les significations détaillées attestées dans les attributs comprennent `PVS` = **Photogrammétrie Satellite**, `ORTHO` = **Orthophotographie**, `TERRAIN_TOPO` = **Levé terrain Topo**. Le terme `AUTRE` ne permet pas de reconstituer une méthode plus précise. Ces modes décrivent la **production GEO PF** et ne disent pas comment ISPF a établi ses propres contours.

Les pièces de contrôle les plus éclairantes sont :

- `IDGeo 20200`, **Hao** : 33,475 km² GEO PF, dont seulement **48,03 %** se situent dans le contour ISPF agrégé de l'unité `202` ;
- `IDGeo 19006`, **Mangareva** : **99,71 %** de la pièce GEO PF se situe dans la géométrie ISPF de `190` ;
- `IDGeo 26300`, **Raroia** : **99,03 %** de la pièce GEO PF est couverte par ISPF `263` ;
- `IDGeo 26401`, **Nihiru** : **89,02 %** de la pièce GEO PF est couverte par ISPF `264`.

Ces proportions révèlent des comportements différents selon les territoires ; il serait impropre de corriger globalement les fonds par un seul traitement topologique.

### Arbitrage éditorial et poursuite

La validation d'identifiants de la PR 83 reste inchangée. **Aucun contour n'est retenu comme référence définitive** sur la seule base d'un écart surfacique ou d'une méthode d'acquisition déclarée.

La prochaine priorité est de **contrôler les polygones de `20200` (Hao)** au niveau des îles, récifs, anneaux et lagons, puis de confronter un cas fortement dissymétrique (`112` ou `263`) pour mettre à l'épreuve l'hypothèse d'emprise lagonaire. Le contrôle devra s'appuyer sur des fonds géographiques et métadonnées documentées, et rester indépendant des références administratives tant que leur généalogie n'est pas établie.
