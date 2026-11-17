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
