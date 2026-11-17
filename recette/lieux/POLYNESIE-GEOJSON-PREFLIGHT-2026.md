# Polynésie française — préflight des trois couches GeoJSON ISPF

**17 novembre 2026 — audit non validant, après la PR 78.**

## Source et périmètre

Le [jeu SIG ISPF](https://www.data.gouv.fr/datasets/limites-geographiques-administratives) a été inventorié dans la [PR 78](https://github.com/nicocoquet/adlfi-referentiels/pull/78). L'archive GeoJSON contient exactement `Com.GeoJSON`, `Comas.GeoJSON`, `Ile.GeoJSON`. Empreinte SHA-256 figée : `6302ad2a17ec1fd8b51f70f1d8ba1501ee7ca212a9cd53c8df4221faedfe0b62`.

Le nouveau script `scripts/auditer_geojson_ispf_polynesie.py` relève, **sans diffusion des contours** : nombre de features, types et présence des géométries, propriétés et types de valeurs, échantillons attributaires, CRS déclaré par le GeoJSON et emprises des coordonnées brutes. Il vérifie l'intégrité de l'archive et compare deux générations identiques du rapport.

## Portée de la recette

Le rapport permet de décider si les couches contiennent des clés explicites et compatibles avec les identifiants ISPF `IDCom`, `IDComas`, `IDIle` ou `CODGEO`. **Aucun appariement n'est validé par cette première lecture**, et les coordonnées sont conservées sous forme brute : le CRS ne peut pas être inféré à partir de la seule plage numérique.

Cette PR ne met en oeuvre **ni moteur topologique, ni réparation automatique, ni reprojection**. Les nombres attendus (48 communes, 98 communes associées, 119 îles) sont des hypothèses de couverture à confronter aux features réelles, pas des assertions a priori. Il peut exister des géométries multiparties ou des objets supplémentaires : l'audit relève d'abord les faits.

## Critères pour la tranche suivante

1. Examiner les résultats effectifs de CI, en particulier les trois schémas et les champs identifiants ;
2. sélectionner des clés de jointure attestées, puis produire une matrice exhaustive des correspondances et non-correspondances avec l'ISPF ;
3. vérifier le CRS avec la métadonnée producteur et le référentiel RGPF ; ne pas déduire le CRS du seul GeoJSON ;
4. utiliser ensuite un moteur spatial spécialisé pour tester validité, auto-intersections, recouvrements, géométries vides, sous-géométries et cas Maria, Raiatea, Tahiti, Gambier, Tahaa ;
5. préserver la divergence documentaire 119/121 et les dates historiques sans rétroprojection.

**Contrat éditorial :** zéro publication de géométrie, zéro ARK, aucune nouvelle autorité, aucune homologation automatique et aucune modification de `docs/`.


## Résultat effectif du préflight CI

La [CI n°44084978229](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44084978229) a réussi les tests synthétiques, la vérification du SHA-256 de l'archive et deux générations identiques du rapport. Le journal confirme :

| Couche | Features | Géométries | Nulles | Vides | Non conformes |
| --- | ---: | --- | ---: | ---: | ---: |
| `Com.GeoJSON` | **48** | 48 MultiPolygon | 0 | 0 | 0 |
| `Comas.GeoJSON` | **116** | 116 MultiPolygon | 0 | 0 | 0 |
| `Ile.GeoJSON` | **119** | 119 MultiPolygon | 0 | 0 | 0 |

Les trois fichiers déclarent `urn:ogc:def:crs:EPSG::4687` et présentent des emprises brutes compatibles entre elles, approximativement de -154,73 à -134,45 en longitude et de -27,90 à -7,86 en latitude. Cette concordance n'est **pas** un contrôle indépendant du datum ou de la précision de la transformation.

Champs de jointure observés dans les attributs :

- `Com` : `IDCom`, `IDSub`, `Commune`, `Sub` ;
- `Comas` : `IDComas`, `IDCom`, `IDSub`, `Comas`, `Commune`, `Sub` ;
- `Ile` : `IDIle`, `IDSub`, `Ile`, `Sub`, `Type`.

**Point méthodologique :** la couche `Comas` comporte 116 objets, non 98. Elle décrit les **116 unités fines ISPF**, soit 98 communes associées effectives et 18 unités conventionnelles non subdivisées ; elle ne doit donc pas être publiée directement comme 116 nouvelles autorités « commune associée ».

Les identifiants sont représentés dans les GeoJSON comme **valeurs numériques**, parfois flottantes (ex. `IDCom: 11.0`). Les jointures devront les normaliser de façon contrôlée, puis vérifier une correspondance univoque et exhaustive avec le XLSX source, sans déduire de code INSEE à partir des noms.

**Non vérifié à ce stade :** unicité des identifiants par couche, correspondance code à code avec les 48/116/119 enregistrements du XLSX, géométries OGC valides, topologie, superposition, harmonisation du millésime et exactitude des découpages historiques.
