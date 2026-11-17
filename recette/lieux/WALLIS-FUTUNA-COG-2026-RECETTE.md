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

La CI exécute les tests synthétiques et compare deux sorties JSON indépendantes octet par octet. **Les dates précises des épisodes ne seront publiées qu'après inspection des résultats réels de la CI.**

## Limites

- **0 nouvelle commune** ;
- **0 alignement Pactols validé à ce stade** ;
- **0 contour historique publié** ;
- **0 succession administrative inférée** ;
- **0 fusion ontologique entre circonscription, royaume coutumier et territoire**.

Phase 2 prévue : après vérification des épisodes exacts, publier les trois **fiches de circonscription** et l'état de `986` dans le module Lieux, puis instruire les éventuelles correspondances Pactols en préservant les catégories institutionnelles.
