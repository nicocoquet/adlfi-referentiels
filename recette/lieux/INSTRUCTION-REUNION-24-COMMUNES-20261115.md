# Lieux AdlFI — La Réunion, 24 communes COG 2026

**15 novembre 2026 · PR #30 · recette documentaire, non validante.**

## Arbitrage complémentaire du 15 novembre 2026 — Le Port (`97407`)

L'éditeur confirme explicitement que le concept Pactols à utiliser pour **Le Port (La Réunion)** est **`26678/pcrtIKvRT9vwUl`**. Il s'agit du candidat principal déjà présent dans la recette : `skos:prefLabel` « Le Port (La Réunion) », URI INSEE déjà déclarée `http://id.insee.fr/geo/commune/97407`.

Cette confirmation lève l'incertitude sur le **choix de l'ARK** face au concept générique « Port » (`26678/pcrtaVzq2EWV3x`) et à l'homonyme « Le Port (Ariège) » (`26678/pcrtuZMn9LuwGy`). Ces deux concepts ne doivent pas être retenus pour la commune réunionnaise.

**Décision enregistrée** : `ARK_CONFIRME_CORRESPONDANCE_A_VALIDER`. La confirmation littérale de l'ARK ne remplace pas l'approbation explicite de la relation Pactols–COG par l'éditeur ; elle n'autorise pas de rétroprojection historique. Les **23 autres décisions restent `A_INSTRUIRE`**.

La section ci-dessous décrit l'état de la **préinstruction initiale** ; consulter le CSV pour l'état actualisé des décisions.

## Résultats du rapprochement

La tranche `recette/lieux/LOT-REUNION-24-COMMUNES-20261115.csv` rassemble **24 codes communaux actuels (97401 à 97424), 24 ARK Pactols distincts** et une URI `http://id.insee.fr/geo/commune/CODE` préexistante dans Pactols pour chacun. Les 24 candidats ont été vérifiés directement dans `candidats_Pactols_integral.csv` (export du RDF Frantiq `Pactols_Lieux_th17_20260722.rdf`) : les ARK porteurs du code sont uniques pour chaque commune, et aucun des 24 concepts n'y est marqué `owl:deprecated`.

Les `skos:prefLabel` sont **identiques aux libellés COG pour 12 communes**, et **qualifiés « (La Réunion) » pour les 12 autres**. Une preuve de code concordant ne vaut pas approbation d'un nouveau lien Pactols–COG.

| Catégorie d'instruction | Communes | Situation |
|---|---:|---|
| Contrôle éditorial standard, sans alerte dans les sources | **21** | Favorables à l'examen individuel au seul millésime COG 2026 |
| Division administrative du 5 février 1965 | **2** | Saint-Louis (`97414`) et Cilaos (`97424`) |
| Concurrence de concepts lexicaux | **1** | Le Port (`97407`) |
| **Total** | **24** | **Aucune décision éditoriale enregistrée par cet audit** |

## Les deux épisodes Saint-Louis / Cilaos

La table officielle `v_mvt_commune_2026.csv` contient, au **5 février 1965**, deux lignes de `MOD=20` décrivant **une seule division administrative** :

- `97414` Saint-Louis → `97414` Saint-Louis (le code subsiste, mais l'emprise se réduit) ;
- `97414` Saint-Louis → `97424` Cilaos (nouveau code communal).

Dans `v_commune_depuis_1943.csv`, le code `97414` apparaît avec le même libellé depuis le **21 mars 1946**. Il ne faut **pas** interpréter cette borne comme la date de création juridique de l'entité actuelle : la [fiche Insee de Saint-Louis](https://www.insee.fr/fr/metadonnees/geographie/commune/97414-saint-louis) donne elle-même le **5 février 1965** comme date de création de la commune dans son contour issu de la division. [La fiche de Cilaos](https://www.insee.fr/fr/metadonnees/geographie/commune/97424-cilaos) confirme la même date.

Conséquence : les deux liens Pactols–COG proposés ne pourront être approuvés qu'au **millésime 2026** tant qu'aucune analyse spatiale historique n'aura été entreprise. **Le maintien du code INSEE et du nom « Saint-Louis » avant/après 1965 ne prouve pas l'identité du périmètre.**

## Le Port : trois concepts Pactols documentés, un seul porteur du bon code

| ARK | `prefLabel` RDF | Qualification |
|---|---|---|
| `26678/pcrtIKvRT9vwUl` | Le Port (La Réunion) | **Candidat principal** : `skos:exactMatch` Pactols vers `http://id.insee.fr/geo/commune/97407` |
| `26678/pcrtaVzq2EWV3x` | Port | Concept non qualifié, sans ce code INSEE ; ne pas identifier à la commune par suppression de l'article |
| `26678/pcrtuZMn9LuwGy` | Le Port (Ariège) | Homonyme d'un autre département ; écarté du lot réunionnais |

Le RDF brut renvoie par ailleurs plusieurs toponymes homonymes pour **11 codes sur les 24**, particulièrement Saint-Denis, Saint-Paul et Sainte-Marie. **Ces résultats bruts ne sont pas onze ambiguïtés éditoriales** : les concepts d'autres départements sont exclus par leur qualificatif, et chaque cible réunionnaise possède **un seul candidat portant le code INSEE de même valeur**. Le Port est conservé comme dossier d'arbitrage parce que « Port » est un homonyme générique, non qualifié.

## Provenance et reproductibilité

- Insee : [COG 2026](https://www.insee.fr/fr/information/8740222), fichiers `v_commune_2026.csv` (SHA-256 `7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3`), `v_commune_depuis_1943.csv` (`08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee`), `v_mvt_commune_2026.csv` (`8b339fad8232e97233af3fd9468715af845e2cf8b14cb67b24d9a301ef8645f1`).
- Pactols-Lieux `th17` du **22 juillet 2026**, RDF intégral Frantiq SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7` ; sous-table des associations candidates SHA-256 `6ec2ea10ba82383cfce644e2b226d194d2c38880499caf777cb131c765e6df4c`.
- Préinstruction 212 communes : SHA-256 `1a2f6868cb8ff6799252d2b2042f8057d2bc826a0e0c15a020be6e18103330cb`.

Une archive de travail de la conversation fournit le classeur de recette à 7 feuilles, les 24 périodes COG, les deux lignes de mouvement, les trois concepts Le Port, le rapport d'empreintes et le script de génération.

**Statut :** `RECETTE_NON_VALIDANTE_NON_PUBLIEE` ; **24 décisions `A_INSTRUIRE`**, aucune nouvelle géométrie historique ni correspondance Pactols–COG publiée. Les décisions de Mayotte demeurent distinctes de celles de La Réunion. La PR #30 reste en brouillon.
