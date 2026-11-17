# Wallis-et-Futuna — préinstruction COG et circonscriptions territoriales

**17 novembre 2026.** Sources : Insee COG 2026 et loi n° 61-814 du 29 juillet 1961.

## Problème de modèle : aucun échelon communal

Le [site institutionnel de Wallis-et-Futuna](https://www.wallis-et-futuna.gouv.fr/Actualites/Presentation-de-Wallis-et-Futuna/Organisation-institutionnelle) confirme explicitement l'absence de communes sur le territoire. L'[article 17 de la loi n° 61-814 du 29 juillet 1961](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000684031) prévoit trois **circonscriptions territoriales** : **Uvea, Alo, Sigave**. L'article 18 les dote de la personnalité morale.

Ces circonscriptions **ne sont pas des communes**. Elles constituent des structures administratives ayant des correspondances avec les trois royaumes coutumiers, mais cette relation ne doit pas effacer leur type administratif distinct.

| Code COG 2026 | Libellé | Type |
| --- | --- | --- |
| `986` | Wallis-et-Futuna | Collectivité/territoire (COMER) |
| `98611` | Alo | Circonscription territoriale (CIR) |
| `98612` | Sigave | Circonscription territoriale (CIR) |
| `98613` | Uvea | Circonscription territoriale (CIR) |

Les trois circonscriptions sont **déjà recherchables dans l'index ultramarin du module Lieux**, sous les identifiants `COMER:CIR:98611`, `COMER:CIR:98612` et `COMER:CIR:98613`. Elles doivent être affichées comme **circonscriptions**, sans enrichir artificiellement les 212 communes actuelles de l'index.

## Deux chronologies à ne pas confondre

L'[Insee, *Codification des collectivités et territoires français d'outre-mer*](https://www.insee.fr/fr/information/7929495), indique :

- les îles Wallis-et-Futuna furent incluses dans des codifications anciennes de l'ensemble calédonien (`98607`), à analyser sans créer une relation d'autorité ;
- la loi statutaire de **1961** est associée au code historique `98609` ;
- le **code `986`** et les **trois codes propres aux circonscriptions** apparaissent dans l'édition **1985** du COG ;
- le territoire est une collectivité d'outre-mer au sens constitutionnel depuis **2003**.

**L'article 17 existe juridiquement depuis 1961**, mais **la première attestation codifiée dans les CSV historiques COG peut être différente**. La période du couple code–libellé COG n'est pas nécessairement l'année de création de la circonscription et n'atteste ni une géométrie rétrospective ni l'identité des codifications anciennes.

Les scripts examinent les **tables officielles originales** sans reconstruire une succession historique entre `98607`, `98609` et `986` à partir des seuls numéros.

## Protocole de vérification

Le script `scripts/auditer_cog_wallis_futuna_2026.py` lit six CSV Insee de l'[archive COG 2026](https://www.insee.fr/fr/information/8740222), protégés par SHA-256, dont les séries COMER actuelles et historiques (`v_comer_2026.csv`, `v_commune_comer_2026.csv`, `v_tom_depuis_1943.csv` et `v_commune_outremer_depuis_1943.csv`).

Il contrôle également l'absence de communes `986*` dans les tables françaises courantes et historiques, et extrait les **épisodes réels** des trois CIR et du territoire, ainsi que les codes anciens à examiner.

La [CI source n°44055036186](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44055036186) a **réussi** le contrôle SHA-256, les tests synthétiques et la génération reproductible de deux rapports JSON. Les états exacts ont été extraits :

| Autorité COG | Début inclusif | Fin exclusive |
| --- | --- | --- |
| `98609` Wallis-et-Futuna | **1961-07-31** | **1985-01-01** |
| `986` Wallis-et-Futuna | **1985-01-01** | En cours |
| `98611` Alo, CIR | **1985-01-01** | En cours |
| `98612` Sigave, CIR | **1985-01-01** | En cours |
| `98613` Uvea, CIR | **1985-01-01** | En cours |

Une réserve déterminante a été confirmée : le code historique `98607` est enregistré sous le libellé **« Nouvelle-Calédonie »**, du **1943-01-01** au **1969-03-30**. Il ne doit pas être publié comme prédécesseur direct de Wallis-et-Futuna.

Ces périodes sont désormais ajoutées sous `docs/data/lieux-wallis-futuna/` et interprétées par `docs/assets/lieux-wallis-futuna-historique.js`. Le script `scripts/verifier_index_public_wallis_futuna_2026.py` vérifie les épisodes publics contre les six fichiers Insee source.

## Limites

- **0 nouvelle commune** ;
- **0 alignement Pactols validé à ce stade** ;
- **0 contour historique publié** ;
- **0 succession administrative inférée** ;
- **0 fusion ontologique entre circonscription, royaume coutumier et territoire**.

**Phase 2 intégrée à la PR :** les trois **fiches de circonscription** et le code territorial `986` affichent leur chronologie documentaire. Un lien de recherche par le code historique `98609` retrouve le dossier du territoire ; aucune autorité Pactols ou commune nouvelle n’est générée. Les correspondances Pactols seront instruites dans un lot ultérieur, distinct de la validation COG.
