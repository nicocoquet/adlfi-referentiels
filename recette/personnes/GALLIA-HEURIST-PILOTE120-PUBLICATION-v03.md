# Personnes — troisième pilote Heurist : publication de 120 autorités et 498 relations

**Visa éditorial obtenu le 28 novembre 2026** sur le dossier privé `AdlFI_Heurist_Personnes_pilote120_v03_PRE_VISA.zip` (« ok, c'est validé »).  
**Portée du visa :** 120 identités et leurs variantes/alignements, 343 nouveaux articles et 498 liens aux publications. Aucune autre candidature Heurist n'est incluse.

## Effectifs et conservation des publications antérieures

| Indicateur | Avant le troisième pilote | Ajout | Après |
|---|---:|---:|---:|
| Autorités `PER` | 322 | **120** | **442** |
| Contributions AdlFI | 1 980 | **0** | **1 980** |
| Notices AdlFI distinctes | 1 779 | **0** | **1 779** |
| Articles Gallia | 352 | **218** | **570** |
| Articles Gallia Préhistoire | 240 | **125** | **365** |
| Articles distincts | 592 | **343** | **935** |
| Relations « auteur » | 788 | **444** | **1 232** |
| Relations « collaborateur » | 123 | **54** | **177** |
| Relations bibliographiques | 911 | **498** | **1 409** |
| Autorités reliées aux articles | 313 | **120** | **433** |

Les 498 relations concernent 450 articles distincts : **107 références déjà publiées** sont réutilisées, **343 nouvelles** sont ajoutées. Les 120 autorités reçoivent les identifiants `PER-000323` à `PER-000442`, avec `contributions_count: 0` : leurs articles ne sont pas interprétés comme des contributions AdlFI. **Aucune modification** des 322 autorités, 1 980 relations AdlFI, 592 articles et 911 relations bibliographiques antérieures ; l'ajout est append-only.

## Provenance et preuve documentaire

- **Archive privée visée :** `AdlFI_Heurist_Personnes_pilote120_v03_PRE_VISA.zip` ; SHA-256 `159b20a18261551ff197ff92662bdfa2ccaef85491d157fdcee5e836ca3b6d81`.
- **Source Heurist privée :** `Export_Revue_Gallia_20261127115832.json` ; SHA-256 `de44407287e2f85132338119354924458320b2dd90cfd4ac30b8b4ee6c44c051`.
- Contrôle indépendant refait après visa : **120/120** identités (PPN modulo 11 et identifiants non partagés), **498/498** relations auteur/collaborateur et positions exactes dans les champs d'article, **343/343** nouveaux articles reconstitués, **592/592** articles publiés auparavant reconstruits à l'identique.
- Les formes de noms, leurs variantes, les identifiants pérennes et les rôles sont ceux de Heurist, sans rapprochement lexical inféré. **18** personnes ont une variante attestée ; celle-ci est décrite sous la catégorie neutre `autre_forme_attestee`.
- Empreintes canoniques SHA-256 des **objets publics effectivement ajoutés** ; méthode : `json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))`, puis SHA-256 UTF-8 :
  - 120 autorités : `630f4a55d01d8f22cb83785270d91fc2ae6caeae583f3f4ead6dcceee5307a99` ;
  - 343 articles : `32520c1b0ca5926fd73dac847fe29e0e05e4352fbf096d6fc806a05af8a428fe` ;
  - 498 relations : `9d2b0fc0e4fabf682ceb56c4142f8613e41a65ef43c7fcb80a304e822735d2be`.
- Le détail `rec_ID` Heurist–`PER` est conservé dans **une archive privée séparée** et non dans le site. Les matrices de visa historiques, initialement `NON_RENSEIGNE`, ne sont pas réécrites rétroactivement.

## Confidentialité et limites documentaires

- **Seules les relations publiables issues des champs Heurist `15` (auteur) et `1057` (collaborateur) sont intégrées.** Les relations et les informations associées au processus interne de validation éditoriale ne sont pas extraites, représentées ou publiées. Aucune donnée personnelle de contexte non nécessaire n'est diffusée.
- Parmi les **343** nouveaux articles : **150 sans DOI**, **6 sans URL**, **3 avec pagination incomplète**. Ces absences restent explicites. Une seule URL historique HTTP a été normalisée en HTTPS (`heurist:1519:73:42141`) ; sa résolution indépendante reste à vérifier.
- Les nouvelles références s'échelonnent de **1943 à 2025**. Les lacunes sont plus fréquentes dans les références historiques ; elles ne constituent pas une preuve d'inexistence des articles.
- Une section bibliographique dépourvue d'URL est rendue sans lien ; une répétition de titre entre plusieurs articles ou années ne suffit pas à les fusionner.
- Le corpus Gallia est **pilote non exhaustif**. Le reliquat à PPN non partagé après ces trois pilotes est **1 779 candidatures** ; les PPN partagés, les fiches sans PPN et l'auteur institutionnel restent à traiter séparément.

## Fichiers de publication et recette

- `docs/data/personnes.json` : ajout de 120 autorités (schéma `0.5.0` maintenu).
- `docs/data/personnes-articles.json` : ajout de 343 articles et 498 relations (schéma `0.1.0` maintenu).
- `docs/data/manifest.json`, `docs/index.html`, `docs/personnes/index.html` : parité et information publique des effectifs.
- `tests/test_personnes_heurist_pilote120_publication.py` : empreintes, non-régression, identifiants, rôles, liens, URL, DOI, compteurs, absence de faux AdlFI.
- `tests/test_personnes_articles_ui.js` : rendu Node des **442 autorités** et **3 389 contributions** toutes revues confondues, y compris les personnes exclusivement bibliographiques et les articles sans URL.

**La CI GitHub valide les transformations et les données de `main` ; elle ne se substitue pas à une recette visuelle réelle du site GitHub Pages déployé.** La recette post-déploiement est suivie dans [l'issue n° 216](https://github.com/nicocoquet/adlfi-referentiels/issues/216). Le suivi de l'extension Heurist est [l'issue n° 217](https://github.com/nicocoquet/adlfi-referentiels/issues/217). Aucun nouveau lot AdlFI n'est ouvert.
