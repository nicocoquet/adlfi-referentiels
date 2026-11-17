# Polynésie française — provenance et préflight des contours SIG

**17 novembre 2026 — audit non validant après fusion de la PR 77.**

## Deux dénombrements ISPF : 119 et 121

La [page officielle des référentiels ISPF](https://www.ispf.pf/ispf/referentiels) annonce **121 îles, dont 75 habitées** et **63 îles rattachées**. Le classeur [Codes géographiques ISPF](https://www.ispf.pf/content/uploads/Codes_geographiques_ce46ed21ee.xlsx) contrôlé dans les PR 75 et 77 fournit **119 codes dans la feuille `Ile`** ; tous les 119 sont présents dans sa feuille `Geo`. Le nombre 63 de la notice ne doit pas être comparé directement aux **64 lignes `isIleRattachee=1`** de `Geo` : une ligne CODGEO n'est pas nécessairement une île unique.

**Décision : divergence documentaire ouverte.** Rien dans ces seuls dénombrements n'identifie deux îles à créer, deux absences ou deux homonymes. Il faut obtenir une liste nominative de la statistique « 121 » ou une règle de comptage avant d'émettre une correction. Un [diagnostic territorial ISPF](https://www.ispf.pf/publication/diagnostic-territorial-2021) emploie lui-même des dénombrements de 119 et de 121 dans sa présentation ; cela ne permet pas d'en expliquer les différences.

## Sources géométriques institutionnelles identifiées

### A — ISPF : limites géographiques administratives (priorité 1)

- [Jeu de données ISPF sur data.gouv.fr](https://www.data.gouv.fr/datasets/limites-geographiques-administratives).
- Producteur : **Institut de la statistique de la Polynésie française**.
- Décrit les contours des **communes, communes associées et îles**, les deux hiérarchies (administrative et géographique) et la **table de relations CodeGeo**.
- Formats annoncés : Shapefile et archives, dont un ZIP GeoJSON du **22 avril 2021**. Jeux de données mis à jour au **10 juin 2022**.
- Licence affichée : **ODbL**. Vérifier les conditions d'attribution et de partage à l'identique avant publication dérivée.
- Archive GeoJSON à auditer : [ressource stable data.gouv.fr](https://www.data.gouv.fr/api/1/datasets/r/f5ec5fb2-c173-4a94-bbd9-c12ec876a4e6).

**Intérêt :** schéma et identifiants très proches de la nomenclature ISPF. **Limites :** géométrie, millésime, projection et correspondances ne sont pas encore homologués dans AdlFI. La date de téléversement n'est pas présumée être une date de validité juridique.

### B — Section Cadastre-Topographie : géographie administrative (priorité 2)

- [Jeu de données GEO PF](https://www.data.gouv.fr/datasets/geographie-administrative-de-la-polynesie-francaise), producteur Section Cadastre-Topographie de la Polynésie française.
- Emprises administratives et îles/atolls/bancs ; **trois ZIP**, mise à jour du **28 février 2022**.
- Licence affichée : **Creative Commons Attribution**.
- Candidat indépendant pour contrôles de cohérence géométrique et toponymique ; les couches exactes, leur schéma et leur historique restent à inventorier.

### C — BD Carto / Te Fenu@ (complément)

- [Section Topographie de la DAF](https://www.service-public.pf/daf/cellule-topo_nosservices/) ; couches de localisation **LOC** (îles, limites administratives), diffusion open data, référentiel géodésique local **RGPF**.
- [Te Fenu@](https://www.service-public.pf/dsi/localisation-cartes/) est le portail SIG de l'administration polynésienne.
- Des couches historiques existent, mais leur présence ne valide pas de contours administratifs anciens.

## Contrôle automatique de cette PR

`scripts/inventorier_sources_sig_polynesie.py` examine le ZIP GeoJSON officiel ISPF :

1. téléchargement par GitHub Actions ;
2. lecture de l'empreinte SHA-256, des chemins, types et tailles des fichiers **sans extraction** ;
3. vérification de l'intégrité de l'archive et garde-fous de taille/chemin ;
4. double génération JSON identique, conservée comme artefact CI hors `docs/`.

**Aucun contour n'est intégré** au site dans ce lot. La suite exigera un audit des géométries et attributs : projection et transformation RGPF/WGS84 documentées, géométries valides, détections de doublons, concordance des `IDComas`/`IDCom`/`IDIle`/`CODGEO`, vérification Maria/Raiatea/Tahiti, contrôle des limites de Tahaa, provenance et millésime de chaque couche. Les géométries multiples ne seront pas fusionnées automatiquement.

## Décision de publication

Cette PR est une **recette de provenance et d'inventaire**, sans création de nouvelle autorité, sans ARK déduit et sans rétroprojection de géométrie moderne vers 1972 ou 1974. Vérifier les résultats réels de CI et la liste d'archives avant la fusion.


## Résultat effectif de la CI d'inventaire — 17 novembre 2026

Le workflow [n°44083686983](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44083686983) est **réussi** (trois tests locaux réussis, archive contrôlée et deux inventaires strictement identiques). Archive GeoJSON ISPF :

- taille : **49 127 691 octets** ;
- SHA-256 : `6302ad2a17ec1fd8b51f70f1d8ba1501ee7ca212a9cd53c8df4221faedfe0b62` ;
- contenu : exactement **`Com.GeoJSON`**, **`Comas.GeoJSON`** et **`Ile.GeoJSON`**.

**Attention :** cette archive ne présente pas de fichier indépendant intitulé `CodeGeo`. La table de relations est décrite par le jeu de données institutionnel mais son intégration effective au ZIP géométrique n'est **pas** démontrée ; il faudra vérifier les attributs de chaque couche et l'existence de la ressource tabulaire distincte. L'étape ultérieure auditerait le nombre de `Feature`, les propriétés, le CRS, la validité des géométries et les clés de jointure avec la nomenclature ISPF.

Aucun de ces trois fichiers n'a été publié dans `docs/`.
