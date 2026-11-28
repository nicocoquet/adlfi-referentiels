# Personnes — sixième lot Heurist : publication de 200 autorités

**Visa éditorial obtenu le 28 novembre 2026** sur l’archive privée `AdlFI_Heurist_Personnes_pilote200_v06_PRE_VISA.zip` (SHA-256 `453687315509827ed2dbc7b6012e407ad91ffaac238bb37513c65e3c1f5832fc`). Les matrices privées ne sont pas publiées.

## Effectifs et conservation

| Indicateur | Avant | Ajout | Après |
|---|---:|---:|---:|
| Autorités `PER` | 802 | 200 | **1 002** |
| Contributions AdlFI | 1 980 | 0 | **1 980** |
| Notices AdlFI | 1 779 | 0 | **1 779** |
| Articles Gallia | 910 | 208 | **1 118** |
| Articles Gallia Préhistoire | 608 | 29 | **637** |
| Articles distincts | 1 518 | 237 | **1 755** |
| Relations « auteur » | 2 150 | 388 | **2 538** |
| Relations « collaborateur » | 289 | 64 | **353** |
| Relations bibliographiques | 2 439 | 452 | **2 891** |
| Autorités reliées à des articles | 793 | 200 | **993** |

Les 452 nouvelles relations portent sur 398 articles distincts, dont **161 articles déjà publiés**, réemployés sans duplication. Les nouveaux identifiants sont `PER-000803` à `PER-001002`. Les 200 autorités ont `contributions_count: 0` : leurs articles ne sont pas des contributions AdlFI. **25** personnes disposent d’une variante attestée, catégorisée `autre_forme_attestee` sans inférence chronologique ou matrimoniale.

## Provenance et recette documentaire

- Source Heurist : export du 27 novembre 2026, SHA-256 `de44407287e2f85132338119354924458320b2dd90cfd4ac30b8b4ee6c44c051`.
- État public de référence : `main` après fusion de la PR #224, commit `7fa268bf054425c9478a73bb14516b88d24c2272` ; blobs de base des catalogues Personnes `7d0dd35e1af1c51ed2ff5fe53de58f3e265656f0` et bibliographique `c8910dc356b3b910814050cb2070fb10bc1cdb02`.
- **200/200** PPN contrôlés et absents des 802 PPN publiés ; aucune fusion lexicale ni collision d’identifiants.
- **452/452** relations contrôlées indépendamment depuis les champs bibliographiques Heurist 15 (auteur) et 1057 (collaborateur), avec rôle et position attestés. **0** répétition exacte dans ce lot.
- Les **802 autorités**, **1 518 articles** et **2 439 relations bibliographiques** antérieurs sont conservés sans mutation (append-only), de même que les **1 980 contributions / 1 779 notices AdlFI**.
- **0** relation orpheline ; **0** collision de PPN, DOI ou URL dans les données projetées.
- Nouveaux articles : **72 DOI absents**, **aucune URL absente**, **aucune pagination incomplète**. Aucune valeur manquante n’est reconstruite artificiellement.

**Deux réserves HTTP→HTTPS :** les références `heurist:1519:73:42134` (DOI `10.4000/galliap.668`) et `heurist:1519:73:42140` (DOI `10.4000/galliap.590`) comportent dans Heurist des URL HTTP historiques converties en HTTPS, sans vérification indépendante de leur résolution à cause du filtrage anti-robots. Les URL restent fondées sur la source, et leur accessibilité doit être vérifiée humainement.

## Contrôles permanents

Le fichier `tests/test_personnes_lot06_heurist_publication.py` verrouille les empreintes canoniques des 200 autorités et des 237 articles / 452 relations nouveaux ; il contrôle leurs identifiants, les rôles, la provenance, la cohérence du manifeste et les lacunes documentaires. Le test Node d’interface est également étendu aux deux nouvelles fiches de bordure.

**Ce procès-verbal public ne contient ni matrices de visa nominatives, ni concordances `rec_ID`–PER, ni experts d’évaluation éditoriale.** Le corpus reste pilote et non exhaustif. La recette visuelle post-déploiement du site GitHub Pages reste distincte de la CI et suivie dans [l’issue #216](https://github.com/nicocoquet/adlfi-referentiels/issues/216). Le suivi des lots Heurist se poursuit dans [l’issue #217](https://github.com/nicocoquet/adlfi-referentiels/issues/217).
