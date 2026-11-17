# Guadeloupe — 35 épisodes communaux COG, 1943–2026

**17 novembre 2026. Publication exclusivement documentaire dans les fiches Lieux.**

## Provenance

Les **35 épisodes code–libellé datés** ont été extraits du **COG 2026 de l'Insee**, fichier `v_commune_depuis_1943.csv`, confronté aux **37 lignes de mouvement** du fichier `v_mvt_commune_2026.csv`. Les deux empreintes SHA-256 des sources conservées par la recette sont respectivement :

- Historique communal : `08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee`.
- Mouvements : `8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1`.

Le script `scripts/verifier_index_public_guadeloupe_2026.py` confronte **toutes les lignes de l'index public** aux épisodes et mouvements de la recette, à chaque exécution spécialisée de GitHub Actions.

Les périodes sont définies par **date de début inclusive et date de fin exclusive**. Le curseur chronologique présente toujours la **situation au 1er janvier de l'année choisie**.

## États au 1er janvier

| Année choisie | Codes communaux actifs dans l'historique COG consulté |
| --- | ---: |
| 1943 et 1946 | 0 — aucun épisode encore ouvert dans le COG exploité |
| 1947 | 34 |
| 1976 | 34, avec le libellé Capesterre-de-Guadeloupe pour 97107 |
| 1977 | 34, avec le libellé Capesterre-Belle-Eau pour 97107 |
| 2007 | 34, dont Saint-Barthélemy (97123) et Saint-Martin (97127) |
| 2008 | 32, hors ces deux anciens codes |
| 2026 | 32, correspondant au COG contemporain du département 971 |

La date du **21 mars 1946** correspond à l'ouverture des premières observations du fichier COG étudié. L'absence d'état au 1er janvier 1946 ne démontre **pas** l'absence d'une commune à cette époque.

## Renommage du 4 juin 1976

Le code **97107** présente deux épisodes documentés :

- Du 21 mars 1946 au 4 juin 1976 : **Capesterre-de-Guadeloupe**.
- À partir du 4 juin 1976 : **Capesterre-Belle-Eau**.

Il s'agit d'un **mouvement MOD 10 du COG**, avec `COM_AV=COM_AP=97107`. La continuité du code est attestée ; elle ne prouve ni continuité géométrique détaillée ni validité rétroactive de l'ARK Pactols actuellement aligné.

## Deux anciennes communes terminées le 23 février 2007

**Saint-Barthélemy**, ancien code `97123`, et **Saint-Martin**, ancien code `97127`, disposent chacune d'un épisode du 21 mars 1946 au **23 février 2007** (fin exclusive).

Le COG des mouvements enregistre pour chacune une ligne du 23 février 2007 sous **MOD 30**, avec **`COM_AP` vide**. On ne peut donc pas présenter le fichier lui-même comme portant une relation codée de successeur vers les collectivités contemporaines `977` et `978`. L'existence de ces collectivités peut être montrée séparément dans le référentiel du COG 2026, **sans postuler l'identité de leurs concepts Pactols avec les anciennes communes 971**.

Le RDF **Pactols Lieux du 22 juillet 2026** étudié dans la recette ne cite **aucune URI INSEE explicite** pour les anciens codes `97123` et `97127`. Les deux fiches historiques sont donc **sans ARK Pactols aligné**. Elles sont recherchables par leur code et leur nom, avec un statut distinct des 32 communes actuelles.

## Complément : succession institutionnelle établie par la loi organique de 2007

Le **champ `COM_AP` du mouvement COG reste vide**, comme documenté ci-dessus. Néanmoins, les [paragraphes X et XI de l'article 18 de la loi organique n° 2007-223](https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000006399955) apportent une **autre preuve** : les collectivités `977` et `978` succèdent **en droit** respectivement aux anciennes communes `97123` et `97127` dans leurs droits et obligations.

Ces deux successions, attestées **par le droit et non inférées d'un champ COG**, sont traitées dans [le module complémentaire des transitions de 2007](../lieux-antilles-collectivites-2007/PROVENANCE.md). Elles ne créent ni code `COM_AP` fictif, ni `skos:exactMatch` Pactols entre autorités historiques, ni continuité géométrique présumée.

## Invariants cartographiques et éditoriaux

- Les **32 correspondances Pactols–COG approuvées pour le millésime 2026** restent inchangées ; aucune n'est prolongée rétroactivement.
- Les deux anciens codes ne sont pas ajoutés dans les communes du COG 2026.
- Aucun **contour historique de Guadeloupe** n'est produit, publié ou attribué à un épisode.
- Aucune **relation de succession** ou correspondance Pactols vers `977` et `978` n'est produite par cette étape.
- Le sélecteur public demeure limité à **Région / Département / Commune**, sans ajout d'un échelon territorial.

Sources : [Insee — Code officiel géographique](https://www.insee.fr/fr/information/2560452) ; [Frantiq — PACTOLS](https://github.com/frantiq/PACTOLS) ; [recette et contrôles](../../../recette/lieux/GUADELOUPE-LOT-01-2026.md).
