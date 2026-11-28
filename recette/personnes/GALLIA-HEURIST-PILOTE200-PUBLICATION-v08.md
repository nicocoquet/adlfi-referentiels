# Personnes — huitième lot Heurist : publication de 200 autorités

**Visa éditorial obtenu le 28 novembre 2026** sur l’archive privée `AdlFI_Heurist_Personnes_pilote200_v08_PRE_VISA.zip` (SHA-256 `6c9e49dc069987de992bf27d7aca892c904e10d1cd099cae3b6ce7553a469779`). Les matrices nominatives et les concordances internes Heurist–PER restent privées.

## Effectifs et conservation

| Indicateur | Avant | Ajout | Après |
|---|---:|---:|---:|
| Autorités `PER` | 1 202 | 200 | **1 402** |
| Contributions AdlFI | 1 980 | 0 | **1 980** |
| Notices AdlFI | 1 779 | 0 | **1 779** |
| Articles *Gallia* | 1 437 | 83 | **1 520** |
| Articles *Gallia Préhistoire* | 666 | 7 | **673** |
| Articles distincts | 2 103 | 90 | **2 193** |
| Relations « auteur » | 3 083 | 241 | **3 324** |
| Relations « collaborateur » | 394 | 20 | **414** |
| Relations bibliographiques | 3 477 | 261 | **3 738** |
| Autorités reliées aux articles | 1 193 | 200 | **1 393** |

Les 261 nouvelles relations concernent 222 articles distincts, dont **132 déjà publiés**, réemployés sans duplication. Les nouveaux identifiants sont `PER-001203` à `PER-001402`. Les 200 autorités ont `contributions_count: 0` : aucune notice ou contribution AdlFI fictive n'est créée. Le présent lot ne comporte aucune variante de nom attestée.

## Provenance et recette documentaire

- Source : export Heurist du 27 novembre 2026, SHA-256 `de44407287e2f85132338119354924458320b2dd90cfd4ac30b8b4ee6c44c051`.
- Base publique de référence : `main` après PR #226, commit `1dee8618180035e9f948c156a56f6835755d697f` ; blobs de base Personnes `7508beb4dad15f7660e3991334cc9851194a8154` et bibliographique `c007872d0b8ff05eefacc81e089ce6227f3af505`.
- **200/200** PPN contrôlés et absents des 1 202 PPN publiés ; aucune fusion fondée uniquement sur la similarité des noms et aucune collision d'identifiants secondaires.
- **261/261** relations contrôlées indépendamment depuis les champs Heurist 15 (« auteur ») et 1057 (« collaborateur »), avec rôle et ordre attestés. **0 mention source redondante**.
- Préservation append-only des **1 202 autorités, 2 103 articles et 3 477 relations** antérieurs, et des **1 980 contributions / 1 779 notices AdlFI**.
- **0** relation orpheline ; **0** collision de PPN, DOI ou URL dans la projection.
- Nouveaux articles : **17 DOI absents** et **1 URL absente** pour `heurist:1519:73:1026`, « Développement et abandon d'un sanctuaire du iiie s. à Sains-du-Nord chez les Nerviens ». La référence doit être affichée sans lien inventé ; aucune pagination incomplète.
- **Épuisement des strates :** aucun candidat éligible sur deux revues, deux rôles, collaborateur *Gallia Préhistoire*, ni avec variante de nom. 96 candidats proviennent du complément conservateur, sans assouplissement du filtre de validation.

## Contrôles permanents

`tests/test_personnes_lot08_heurist_publication.py` verrouille par SHA-256 canonique les 200 autorités, 90 articles et 261 relations publiés. Il vérifie leurs identifiants, les rôles, le manifeste, les lacunes documentaires et la non-régression. `tests/test_personnes_articles_ui.js` vérifie les fiches extrêmes, la distinction des rôles et l'absence de notices AdlFI fictives. Les tests de tous les lots précédents restent actifs.

**Protection des données :** le dépôt ne contient ni matrices privées de visa, ni export brut Heurist, ni champs d'expertise éditoriale ou concordances internes Heurist–PER. Le corpus reste pilote, progressif et non exhaustif. La recette visuelle post-déploiement du site GitHub Pages reste distincte de la CI et suivie dans [l’issue #216](https://github.com/nicocoquet/adlfi-referentiels/issues/216). Le suivi des lots Heurist reste dans [l’issue #217](https://github.com/nicocoquet/adlfi-referentiels/issues/217).
