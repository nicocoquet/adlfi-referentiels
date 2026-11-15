# Lieux AdlFI — Mayotte, instruction des 17 communes actuelles (COG 2026)

**15 novembre 2026 — PR #30 — préconisations non validantes.**

## Sources et preuve commune par commune

La tranche `recette/lieux/LOT-MAYOTTE-17-COMMUNES-20261115.csv` contient les **17** couples code INSEE / ARK Pactols, avec champs de décision laissés à `A_INSTRUIRE`. Les sources rapprochées sont :

1. `v_commune_2026.csv` — communes officielles, Insee COG 2026 ; SHA-256 `7be1153de3a63df48fa0ca77f8490c8a0c5c9c4eb12f5cec1ca7f70b0237b1d3`.
2. `v_commune_depuis_1943.csv` — périodes communales DROM ; SHA-256 `08c532ed8dade0a048aa4e1d72b8a25852a3aa05ce79c7911276031235d6eeee`.
3. `v_commune_outremer_depuis_1943.csv` — périodes COMER des subdivisions ; extraction qualifiée `zonages_historiques.csv`, SHA-256 `53c2fe2bf44718f105403b51b232560fc8381de000688f3d3ebbc37dfa99b19d`.
4. Pactols-Lieux, export intégral Frantiq `th17` du **22 juillet 2026** ; SHA-256 RDF `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`. Extraction contrôlée des candidatures : SHA-256 `6ec2ea10ba82383cfce644e2b226d194d2c38880499caf777cb131c765e6df4c`.
5. CSV initial de préinstruction Mayotte : SHA-256 `db22dd7575e7024977723d09c1fc7da2d608689ce73159603821749c9f7206b6`.

Le contrôle par code établit : 17 codes communaux actuels `97601` à `97617`, 17 labels identiques entre COG et `skos:prefLabel`, 17 URI `http://id.insee.fr/geo/commune/CODE` déjà déclarées par `skos:exactMatch` dans le concept Pactols, 17 concepts non marqués comme `owl:deprecated`, aucun ARK concurrent pour le même code dans ce lot.

**Attention :** une assertion `skos:exactMatch` déjà présente dans Pactols est une preuve documentaire de liaison déclarée par ce thésaurus, **pas** une nouvelle relation homologuée par AdlFI.

## Correction majeure des bornes temporelles

La première préinstruction ne citait que la série **DROM depuis le 31 mars 2011**. La vérification de la **seconde famille officielle de fichiers COG** établit cependant pour chacun des mêmes 17 codes :

| Série | Début inclus | Fin exclue | Nature |
|---|---|---|---|
| `v_commune_outremer_depuis_1943.csv` | **2007-02-23** | **2011-03-31** | `COM` dans les subdivisions du territoire ultramarin (COMER) |
| `v_commune_depuis_1943.csv` | **2011-03-31** | Encore en cours au COG 2026 | `COM` dans la série communale DROM |

Les libellés et les codes communaux restent identiques au passage d'une série à l'autre.

**Le 31 mars 2011 n'est pas la date de création des 17 communes**, mais le changement de statut de Mayotte et de famille de données administratives. De même, la borne 2007 documente l'entrée dans cette série COG : elle ne constitue pas, à elle seule, une preuve de création effective de la municipalité à cette date.

Le code institutionnel de Mayotte devient `976R` au **1er janvier 2026** ; il ne doit pas être confondu avec les codes communaux `97601` à `97617`. Source : [Insee, collectivités à statut particulier](https://www.insee.fr/fr/information/7929497).

Les **34 épisodes** (17 COMER + 17 DROM) sont exposés dans l'archive éditoriale de la conversation et pourront alimenter la chronologie du futur module mondial sans projeter rétroactivement des géométries de 2026.

## Propositions de validation

| État proposé | Communes | Décision |
|---|---:|---|
| Favorable à une validation Pactols–COG **au seul millésime 2026** | **16** | Confirmation éditoriale à obtenir |
| Favorable sous réserve du contrôle de résolution de l'ARK | **1 : Dembeni, 97607** | L'ARK source est `26678/crtZcuFSJVYZU` et commence par `crt`, non par `pcrt` |
| **Approbations nouvelles dans le référentiel** | **0** | `A_INSTRUIRE` pour les 17 lignes |

La forme `26678/crtZcuFSJVYZU` de Dembeni est **attestée telle quelle dans le RDF Frantiq** et porte le bon `prefLabel` et l'URI INSEE `97607`. Aucun préfixe `p` ne doit être inséré par conjecture. La résolution actuelle de cet ARK n'a pas été vérifiée.

La portée des correspondances proposées est `correspondance_communale_validee`, **millésime COG 2026 uniquement après approbation**, sans déclaration d'identité absolue entre le concept documentaire et tous les états anciens de l'administration.

## État du chantier

Les 17 lignes détaillées sont versionnées **sous `recette/` uniquement**. L'archive de travail comporte un XLSX à quatre feuilles, les 17 candidats, 34 épisodes administratifs et les empreintes des fichiers sources. **Aucun élément de `docs/` n'est modifié, aucune validation individuelle n'est prononcée par cet audit.**

Prochaine opération : arbitrage éditorial des 16 couples standards, vérification de l'ARK Dembeni, puis export public **après validation** seulement.
