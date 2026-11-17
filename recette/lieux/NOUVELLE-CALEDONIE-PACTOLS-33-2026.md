# Nouvelle-Calédonie — audit Pactols–COG des 33 communes 2026

**17 novembre 2026 — instruction RDF de référence, sans publication d'ARK.**

## Périmètre

Le socle [COG Nouvelle-Calédonie](NOUVELLE-CALEDONIE-COG-HISTORIQUE-2026-RECETTE.md) publié contient **33 communes** de code `988xx` au millésime `2026-01-01`, sans alignement Pactols communal encore validé. Les trois provinces, les huit aires coutumières et l'autorité territoriale 988 sont des catégories distinctes. **Poya (98827)** relève de deux provinces ; **Kouaoua (98833)** possède un épisode communal COG ouvert le 25 avril 1995 (division de Canala). Ces observations historiques ne valident aucun lien Pactols.

## Sources et traitement

- **RDF Pactols Lieux** : dépôt `frantiq/PACTOLS`, commit `69bf9697e24cefd645a69465bbd271702786285a`, fichier `Pactols_Lieux_th17_20260722.rdf`, SHA-256 `3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7`.
- **COG INSEE 2026** : six tables originales à SHA-256 vérifiés selon `scripts/auditer_cog_polynesie_2026.py`. L'audit historique de Nouvelle-Calédonie valide leurs 33 codes et libellés contre l'index COG publié.

Le script `scripts/auditer_pactols_nouvelle_caledonie_2026.py` récupère les `skos:exactMatch` typés `http(s)://id.insee.fr/geo/commune/988xx`, ARK source, libellé français, variantes, dépréciations, remplacements et autres URI INSEE éventuellement portées par le même concept. Il réutilise le parseur RDF en flux déjà testé pour la Polynésie.

**Seules** les assertions `skos:exactMatch` explicites, uniques et non dépréciées, associées à un concept dont le libellé correspond à la commune administrative, sont classées `ELIGIBLE_SELON_REGLE`. Les autres états sont `A_INSTRUIRE_MULTIPLICITE`, `A_INSTRUIRE_ONTOLOGIE_OU_DIVERGENCE` ou `SANS_ASSERTION_EXPLICITE`. Un homonyme lexical reste diagnostique et ne crée jamais d'identifiant validé.

## Points d'attention éditoriaux

- Les libellés « île », « îlot », « archipel », « atoll », « district » et « royaume » déclenchent un contrôle de catégorie même en présence d'une assertion INSEE explicite.
- Les tribus et aires coutumières néo-calédoniennes ne deviennent pas des communes par homonymie ; les subdivisions et les provinces ne sont pas associées automatiquement aux ARK des communes.
- Un concept exactMatch vers plusieurs codes, une famille d'URI autre que `geo/commune`, une dépréciation, ou un désaccord de libellé reste **à instruire**.
- Ne pas transférer l'autorité de Canala à Kouaoua : l'épisode COG de 1995 est une preuve d'évolution administrative, pas de synonymie d'identifiant.
- Les dates de première attestation dans le COG n'établissent pas nécessairement les dates historiques de création des collectivités.

## Livraison et décision

La CI `lieux-nouvelle-caledonie-pactols-2026.yml` contrôle les sources par SHA-256, exécute deux fois la qualification des 33 codes et archive le rapport JSON sous les artefacts de recette. Les nombres d'assertions réellement trouvées et les ARK seront consignés **après le premier calcul effectif** : aucune cardinalité Pactols n'est supposée.

**Aucune publication d'ARK, de lien, de toponyme ou de géométrie dans cette PR.** Toute décision de validation fera l'objet d'un registre éditorial et d'une recette de publication séparée.


## Résultats vérifiés sur les données réelles — 17 novembre 2026

L'exécution [GitHub Actions n°44150401473](https://github.com/nicocoquet/adlfi-referentiels/actions/runs/44150401473) a vérifié les empreintes des **six tables COG** et du **RDF Pactols**, puis obtenu deux rapports identiques octet à octet.

| Contrôle | Résultat |
| --- | ---: |
| Communes COG Nouvelle-Calédonie au 1er janvier 2026 | **33** |
| Codes cités par `skos:exactMatch` communal dans Pactols | **33/33** |
| Concepts `exactMatch` recensés | **33** |
| Couples éligibles selon la règle générale | **32** |
| Cas nécessitant instruction de catégorie/libellé | **1** |
| Candidats seulement lexicaux sans URI pour ces 33 codes | **0** |
| Alignements publiés par cet audit | **0** |

### Cas restant à arbitrer : `98809` — L'Île-des-Pins

Le [concept Pactols `26678/pcrti4LqTHByEs`](https://ark.frantiq.fr/ark:/26678/pcrti4LqTHByEs) possède :

- un `skos:exactMatch` explicite vers `http://id.insee.fr/geo/commune/98809` ;
- un **`prefLabel` « Île-des-Pins »**, désignant potentiellement un objet insulaire ;
- un **`altLabel` « L'Île-des-Pins »**, qui concorde avec le nom de la commune COG 2026 ;
- aucune dépréciation, aucun remplacement ni autre URI INSEE concurrente dans l'export étudié.

Le lien est donc **fortement étayé mais non automatiquement accepté** : le `prefLabel` pourrait décrire l'île géographique plutôt que la commune administrative. Le `altLabel` identique au libellé administratif et le `exactMatch` constituent des éléments favorables, mais ne lèvent pas formellement la question de la **nature de l'autorité Pactols**. Il faudra un arbitrage éditorial ou une correction explicite de la notice Pactols, comme pour Saint-Pierre, sans généraliser une équivalence automatique île↔commune.

### Conséquence opérationnelle

Les **32 autres codes** sont éligibles à une validation dans un **registre versionné** et à une publication contrôlée ; le code **`98809`** doit rester à instruire, sans être perdu du référentiel ni comptabilisé comme validé. Cette distinction vise la **qualité des identifiants 2026**, pas l'homologation des contours : notamment, la géométrie 2026 de **Dumbéa (98805)** était encore signalée invalide dans les contrôles précédents et **n'est pas corrigée** par l'admissibilité de son ARK.
