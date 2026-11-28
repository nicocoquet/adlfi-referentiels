# Personnes — quatrième lot Heurist : publication de 160 autorités

**Visa éditorial obtenu le 28 novembre 2026** sur l’archive privée `AdlFI_Heurist_Personnes_pilote160_v04_PRE_VISA.zip`, SHA-256 `491df7230da17894173d8e8e387dc180d27a7fc85e76b645eaf29b296797727f`.

## Effectifs et conservation

| Indicateur | Avant | Ajout | Après |
|---|---:|---:|---:|
| Autorités PER | 442 | 160 | 602 |
| Contributions AdlFI | 1 980 | 0 | 1 980 |
| Notices AdlFI | 1 779 | 0 | 1 779 |
| Articles Gallia | 570 | 277 | 847 |
| Articles Gallia Préhistoire | 365 | 74 | 439 |
| Articles | 935 | 351 | 1 286 |
| Relations auteur | 1 232 | 499 | 1 731 |
| Relations collaborateur | 177 | 52 | 229 |
| Relations bibliographiques | 1 409 | 551 | 1 960 |
| Autorités reliées aux articles | 433 | 160 | 593 |

Attribution des identifiants `PER-000443` à `PER-000602`, sans création de contribution AdlFI fictive. Les 147 références préexistantes sont réutilisées ; les 442 autorités, 935 articles et 1 409 relations antérieurs sont préservés à l’identique. La nouvelle source contient 552 mentions, dont une répétition exacte dédupliquée pour produire 551 relations distinctes.

## Provenance et protection des données

Export Heurist du 27 novembre 2026, SHA-256 `de44407287e2f85132338119354924458320b2dd90cfd4ac30b8b4ee6c44c051`. Identités, PPN, alignements et liens examinés sur les matrices privées du lot v0.4 ; les données publiques sont limitées aux autorités, articles et relations auteur/collaborateur. Les correspondances internes Heurist–PER, champs d'évaluation éditoriale et matrices nominatives ne sont pas joints au dépôt.

## Contrôles

- 160 PPN distincts et sans collision avec les 442 autorités précédentes ; 30 personnes avec variantes attestées.
- 351 nouveaux articles sans collision de DOI ou URL ; 146 sans DOI, 5 sans URL, une pagination incomplète.
- 551 liens auteur/collaborateur : 499 auteur, 52 collaborateur ; 498 articles distincts liés et 147 articles réutilisés.
- Référentiel AdlFI inchangé : 1 980 contributions pour 1 779 notices.
- Aucun lien orphelin et 593 personnes distinctes reliées à une publication.

**Recette CI et visuelle :** à vérifier sur la PR et sur GitHub Pages après déploiement, conformément à [l’issue #216](https://github.com/nicocoquet/adlfi-referentiels/issues/216). Suivi du lot dans [l’issue #217](https://github.com/nicocoquet/adlfi-referentiels/issues/217).
