# Personnes — septième lot Heurist : publication de 200 autorités

**Visa éditorial obtenu le 28 novembre 2026** sur l’archive privée `AdlFI_Heurist_Personnes_pilote200_v07_PRE_VISA.zip` (SHA-256 `7791399b2ca337cc51eeaf8e33a0e871701e789fdbee94ebe68c216542c9d8a2`). La publication ne comprend que les champs publics prévus ; les matrices nominatives et les correspondances internes Heurist–PER restent privées.

## Effectifs et conservation

| Indicateur | Avant | Ajout | Après |
|---|---:|---:|---:|
| Autorités `PER` | 1 002 | 200 | **1 202** |
| Contributions AdlFI | 1 980 | 0 | **1 980** |
| Notices AdlFI | 1 779 | 0 | **1 779** |
| Articles Gallia | 1 118 | 319 | **1 437** |
| Articles Gallia Préhistoire | 637 | 29 | **666** |
| Articles distincts | 1 755 | 348 | **2 103** |
| Relations « auteur » | 2 538 | 545 | **3 083** |
| Relations « collaborateur » | 353 | 41 | **394** |
| Relations bibliographiques | 2 891 | 586 | **3 477** |
| Autorités reliées aux articles | 993 | 200 | **1 193** |

Les 586 nouvelles relations concernent 530 articles distincts, dont **182 articles antérieurs réutilisés** sans duplication. Les nouveaux identifiants sont `PER-001003` à `PER-001202`. Les 200 autorités ont `contributions_count: 0` : leurs articles bibliographiques ne créent aucune contribution fictive dans AdlFI. **8 profils** comportent une variante de nom attestée (type `autre_forme_attestee`), sans inférence historique ou matrimoniale.

## Provenance et recette documentaire

- Source : export Heurist du 27 novembre 2026, SHA-256 `de44407287e2f85132338119354924458320b2dd90cfd4ac30b8b4ee6c44c051`.
- État public de référence : `main` après PR #225, commit `d377c2406edfed575d4a769e08912fe38f974266` ; blobs de base Personnes `10f71e9bf7555b152d5b568779914e8cbc4bbac7` et bibliographique `1f73afd2f37330324e1031508ede6f5e4c80fd21`.
- **200/200** PPN contrôlés par modulo 11 ; aucun PPN ni identifiant secondaire déjà attribué à une autre entrée Heurist. Aucune fusion sur seule ressemblance de nom.
- **586/586** relations contrôlées indépendamment depuis les champs Heurist 15 (`auteur`) et 1057 (`collaborateur`) : rôle et position attestés. **0 mention source redondante** dans ce lot.
- Préservation `append-only` des **1 002 autorités, 1 755 articles et 2 891 relations** antérieurs, ainsi que des **1 980 contributions / 1 779 notices AdlFI**.
- **0** relation orpheline ; **0** collision de PPN, DOI ou URL dans les données de publication.
- Nouveaux articles : **141 sans DOI** ; aucune URL manquante, aucune pagination incomplète et aucune nouvelle normalisation historique HTTP→HTTPS. Les lacunes ne sont pas comblées artificiellement.
- **Stratification conservatrice :** absence de candidat admissible « deux revues » et de collaborateur Gallia Préhistoire dans le reliquat admissible ; 41 candidats de complément. Ce biais documentaire est déclaré, sans assouplissement des règles d'identité.

## Contrôles permanents

Le fichier `tests/test_personnes_lot07_heurist_publication.py` verrouille par SHA-256 canonique les 200 autorités, 348 articles et 586 relations nouvellement publiés. Il contrôle les PPN, les effectifs, les rôles, la conservation AdlFI, la complétude bibliographique et le manifeste ; le test Node `tests/test_personnes_articles_ui.js` vérifie les deux fiches extrêmes sans notices AdlFI fictives. Les tests des lots antérieurs restent actifs.

**Protection des données :** le dépôt ne contient ni matrices nominatives de visa, ni export brut Heurist, ni champs d'expertise de validation éditoriale. Le catalogue bibliographique reste pilote, progressif et non exhaustif. La recette visuelle post-déploiement du site GitHub Pages reste distincte de la CI et suivie dans [l’issue #216](https://github.com/nicocoquet/adlfi-referentiels/issues/216). Le suivi des lots Heurist se poursuit dans [l’issue #217](https://github.com/nicocoquet/adlfi-referentiels/issues/217).
