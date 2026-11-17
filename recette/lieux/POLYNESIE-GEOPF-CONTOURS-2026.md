# Polynésie française — comparaison de contours GEO PF–ISPF (PR 84)

**17 novembre 2026 — recette non validante.** Cette tranche suit les PR 80–83, désormais fusionnées sur `main`.

## Sources figées et statut

| Source | SHA-256 |
| --- | --- |
| Classeur ISPF, nomenclature géographique | `d84f9a69f2c64f744ee0719b01c4841953019d45a1fb29b8abb0db2f3f0176e6` |
| Archive GeoJSON ISPF, couche `Comas` | `6302ad2a17ec1fd8b51f70f1d8ba1501ee7ca212a9cd53c8df4221faedfe0b62` |
| Archive SHP GEO PF `loc_commune_associee`, 28 février 2022 | `29230c18487385f84ca480e9b2c921ea389f848663a4a9574e77b9cbbf40db7b` |

Les deux sources géométriques déclarent RGPF/GRS 1980. **Leur indépendance n'est pas démontrée**, et le millésime de publication d'une archive ne constitue pas automatiquement le millésime de levé.

## Méthode

La feuille ISPF `Geo` contient **179 unités géographiques** et permet un regroupement vers les **116 unités fines** de la couche `Comas`.

Le script `scripts/comparer_contours_geopf_ispf.py` ne joint une pièce GEO PF que si `code_geogr=IDGeo` **et** si toutes les clés `IDComas`, `IDCom`, `IDSub`, `IDIle` concordent. Les codes ne sont jamais rapprochés par libellé. Une unité fine n'est comparée que si **tous** ses codes `IDGeo` attendus sont présents et cohérents dans GEO PF.

Les quatre discordances de la PR 83 sont traitées comme **exclusions documentaires**, sans forcer les codes :

- `43001/43101` : Maria, partie Rimatara ;
- `44001/44301` : Maria, partie Rurutu ;
- `IDGeo 28001` : Maupihaa (codes insulaires `53`/`54`) ;
- `IDGeo 55001` : Fangataufa (codes insulaires `20`/`113`).

Pour chaque unité éligible, les géométries GEO PF sont agrégées avec `unary_union`, puis confrontées à la géométrie `Comas` ISPF : égalité topologique, surface de différence symétrique et proportion de différence par rapport à l'union. Les surfaces sont mesurées **sur l'ellipsoïde GRS 1980** par `pyproj.Geod`. Les unités ayant des géométries invalides sont **écartées**, sans réparation par `make_valid` ou `buffer(0)`.

Enfin, seules les paires parmi les unités GEO PF entièrement appariées sont examinées pour les recouvrements d'intérieur. Les mesures manquantes du fait des exclusions **ne sont jamais interprétées comme une disparition des recouvrements précédemment identifiés dans ISPF**.

## Précautions

- Les surfaces de différence symétrique ne doivent pas être interprétées comme une erreur juridiquement démontrée ; les fonds peuvent représenter différemment le littoral, les îlots ou les limites.
- Les différences de découpage temporel et de généalogie géométrique restent à étudier.
- Pas de correction de contours ni de publication sur GitHub Pages ; les résultats restent dans un artefact GitHub Actions et une note de recette.
- **Ne pas fusionner avant vérification des journaux CI et qualification des exclusions.**
