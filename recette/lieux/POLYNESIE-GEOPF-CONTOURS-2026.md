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


## Résultats de l'exécution initiale

Le workflow spécialisé [n°44105618773](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44105618773) est **réussi** : téléchargement et SHA des trois sources conformes, double calcul reproductible, artefact JSON de comparaison sans polygones.

**112 des 116 unités fines** sont comparées après contrôle exhaustif de leurs `IDGeo` constitutifs. Quatre unités sont délibérément exclues :

| `IDComas` exclu | Motif | Pièces géographiques manquantes du jeu de comparaison |
| --- | --- | --- |
| `280` | Code d'île divergent pour Maupihaa (Mopelia) | `28001` |
| `431` | Convention de code géographique différente, Maria/Rimatara | `43001` |
| `441` | Convention de code géographique différente, Maria/Rurutu | `44001` |
| `550` | Code d'île divergent pour Fangataufa | `55001` |

Au sein des **112 unités GEO PF complètes et appariées**, l'audit ne trouve **aucune paire en recouvrement surfacique**. Ce résultat ne vaut **pas** pour les quatre unités exclues et ne prouve pas que les 65 paires relevées dans ISPF soient des anomalies juridiquement avérées. Les deux sources peuvent appliquer un mode de représentation différent.

### Écarts de contours les plus importants

| `IDComas` | Aire GEO PF | Aire ISPF | Différence symétrique | Part de la différence dans l'union |
| --- | ---: | ---: | ---: | ---: |
| `190` | 59,608 km² | 94,134 km² | **35,313 km²** | **37,36 %** |
| `202` | 44,305 km² | 44,303 km² | **34,851 km²** | **56,46 %** |
| `112` | 13,975 km² | 40,853 km² | **27,389 km²** | **66,63 %** |
| `263` | 16,527 km² | 38,862 km² | **22,666 km²** | **58,08 %** |
| `264` | 12,735 km² | 31,550 km² | **20,654 km²** | **63,61 %** |

Une différence symétrique importante peut correspondre à des îles ou îlots différents, un contour littoral différent, une dissymétrie temporelle, ou une origine cartographique différente. **Le cas `202` est particulièrement révélateur** : les surfaces globales de chaque représentation sont quasiment identiques (environ 44,3 km²), mais leur superposition est insuffisante pour conclure à une même géométrie. L'écart ne saurait être attribué à un simple problème de surface totale.

**Arbitrage méthodologique :** ne publier ni ne corriger aucun de ces contours. La prochaine instruction doit contrôler ce que représentent les ensembles de polygones de chaque `IDComas` et les métadonnées de production, avant toute substitution GEO PF → ISPF. La précision et l'indépendance des géométries restent non établies.
