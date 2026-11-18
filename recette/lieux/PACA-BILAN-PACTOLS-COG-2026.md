# PACA — bilan actualisé du référentiel des communes COG et des autorités Pactols (2026)

**17 novembre 2026. Audit de recette, sans publication de liens supplémentaires.**

## Question

Le pilote Provence-Alpes-Côte d'Azur possède **103 autorités Pactols éditorialement validées**, tandis que le `cog-paca.json` et la couche communale 2026 recensent **946 communes**. Ces deux effectifs ne représentent pas le même périmètre : les 103 autorités proviennent du pilote de l'atlas AdlFI, pas d'un inventaire régional exhaustif des `skos:exactMatch` de Pactols.

Les 946 contours 2026 sont déjà publiés et ont leur provenance géométrique, distincte des 103 alignements éditoriaux. **Il faut donc analyser la couverture Pactols avant de proposer une extension de l'index**, et ne pas interpréter 843 fiches sans ARK validé comme une absence de concept Pactols.

## Recette

Le script `scripts/auditer_paca_pactols_cog_2026.py` croise le COG Insee au 1er janvier 2026 (REG=93, six départements 04, 05, 06, 13, 83, 84), les 103 validations éditoriales `docs/data/lieux.json` et le RDF Pactols-Lieux du 22 juillet 2026, sources contrôlées par empreintes.

Pour chaque commune : statut d'éligibilité d'un exactMatch explicite vers le code INSEE, candidats lexicaux non validants, statut du pilote, ARK du pilote et présence/absence de son exactMatch dans le RDF. Les divergences ne remettent **pas** automatiquement en cause la décision éditoriale initiale. L'ensemble des candidats supplémentaires reste NON_PUBLIE, en attente d'une recette des URI INSEE concurrentes et d'un registre de publication distinct.

Le rapport est reproductible deux fois et publié comme artefact GitHub Actions hors `docs/`. Aucun nouveau lien, contour, code COG historique ou ARK ne sera créé par cette PR.

## Questions subséquentes

Il faudra distinguer : couverture communale au COG 2026, couverture des ARK Pactols de l'export RDF et couverture des autorités *effectivement utilisées dans les notices AdlFI* (corpus de 9 928 autorités à l'échelle nationale), puis examiner les communes nouvelles et les codes hérités sans inférer de relation historique.


## Résultat effectif de l'audit sur sources épinglées (17 novembre 2026)

Le [workflow n°44183508914](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44183508914) est réussi et les deux rapports sont identiques octet à octet.

- **946** communes PACA (COG 2026) ; **103** correspondances éditoriales du pilote, toutes retrouvées sur le même code par exactMatch dans le RDF.
- RDF : **934** communes éligibles par la règle stricte ; **8** cas à plusieurs ARK, **3** divergences libellé/statut/URI, **1** sans exactMatch.
- **832** communes éligibles **hors des 103 autorités du pilote** : elles correspondent au potentiel immédiat d'enrichissement, encore non publié et soumis au préflight des URI concurrentes.
- **11** communes non éligibles hors pilote ; **une** autorité déjà validée éditorialement dans les 103 n'entre pas dans le statut éligible par la règle automatisée, malgré la présence de son exactMatch. Cette décision n'est pas invalidée automatiquement : le dossier est à qualifier.
- **0 nouveau lien ou contour publié** dans cette PR.

Important : les nombres 934 et 103 ne s'additionnent pas. Les correspondances retenues dans le pilote font partie de la couverture RDF à l'exception de la différence de classification signalée ci-dessus. Ce premier audit ne garantit pas encore que tous les nouveaux candidats soient indemnes d'URI INSEE supplémentaires non reconnues par le parseur ; la vérification exhaustive précède toute publication.


### Dossiers exceptionnels identifiés dans le RDF épinglé

**Huit codes présentent plusieurs concepts ARK** : Ubaye-Serre-Ponçon (04033), Val d'Oronaye (04120), Valdoule (05024), Aubessagne (05039), Garde-Colombe (05053), Vallouise-Pelvoux (05101), Val Buëch-Méouge (05118), **Dévoluy (05139)**.

**Trois codes présentent une divergence de libellé, statut ou URI** : Abriès-Ristolas (05001), Rousset-Serre-Ponçon (05127), Esparron-de-Pallières (83052).

**Un code n'a pas d'exactMatch vers la forme INSEE à code reconnue** : Céreste-en-Luberon (04045).

**Dévoluy (05139)** est un dossier particulier : l'autorité `26678/pcrtSeD2WMEIYA` a déjà été approuvée dans les 103 décisions du pilote et est toujours citée par exactMatch ; le même code est aussi revendiqué par `26678/pcrt2XYqgMPgx5`. Il ne faut ni supprimer la validation éditoriale antérieure ni publier le second ARK comme une identité supplémentaire sans arbitrage. Ce cas explique pourquoi **934 éligibles par la règle automatique** ne signifie pas exactement **103 validations du pilote + 832 nouveaux éligibles** : seuls 102 des 103 pilotes sont dans la sous-catégorie éligible, le 103e étant Dévoluy.

Les **11 dossiers hors pilote** sont exclus de l'extension proposée. Leurs codes sont 04033, 04045, 04120, 05001, 05024, 05039, 05053, 05101, 05118, 05127 et 83052.


## Consolidation complémentaire — 18 novembre 2026

La [PR n°119](https://github.com/nicocoquet/adlfi-referentiels/pull/119) a achevé le **préflight exhaustif de toutes les URI INSEE** du snapshot Pactols, y compris les UUID et URI concurrentes initialement omises par le parseur :
- **832/832** nouveaux candidats PACA conformes après contrôle ; **0 mise en quarantaine** ;
- les **103 décisions éditoriales du pilote** restent valides, sans réinterprétation des anciens codes ni des 1 116 épisodes COG ;
- **11 codes** restent exclus de l'enrichissement et à instruire, dont les sept communes nouvelles avec plusieurs ARK, trois divergences de libellé ou de statut, et Céreste-en-Luberon sans exactMatch reconnu ;
- **Dévoluy (05139)** conserve la validation `26678/pcrtSeD2WMEIYA` du pilote, malgré la concurrence RDF d'un autre ARK.

Registre : `recette/lieux/PACA-CANDIDATS-EXACTMATCH-2026.csv` (SHA-256 `647ba3e1fdfd80199b854b512f12269379edaf910f47e34b7f53650ce2844925`), avec preuves individuelles et provenance. Rapport : `recette/lieux/PACA-PREFLIGHT-EXACTMATCH-2026.json` (SHA-256 `a1d032da4c06a69c7d77ec8b6d28977856cc1e22bec1260d5d8e8550303c5a22`).

La [PR n°120](https://github.com/nicocoquet/adlfi-referentiels/pull/120) porte la **publication complémentaire de 832 alignements**, dans un index distinct des 103 autorités du pilote et des chronologies COG. Le potentiel consolidé est donc **935 identités Pactols–COG de communes PACA au millésime 2026**. Le sens du lien est strictement documentaire : un exactMatch explicite univoque vers l'URI INSEE courante ; **aucune identité historique, succession COG ou géométrie ancienne n'en découle**. La liste des 11 exceptions est conservée séparément.
