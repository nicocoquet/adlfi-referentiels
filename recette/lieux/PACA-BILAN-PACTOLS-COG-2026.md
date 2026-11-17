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
