# Personnes — deuxième pilote de publication Heurist : 80 autorités et 333 liens

**État :** publication du deuxième ensemble d'autorités Heurist dans le référentiel commun AdlFI / Gallia / Gallia Préhistoire.  
**Décision éditoriale :** accord de continuation du 28 novembre 2026, donné en réponse au dossier de visa `AdlFI_Heurist_Personnes_pilote80_v02_PRE_VISA.zip`.  
**Périmètre :** les 80 identités, leurs alignements et variantes, les 191 articles nouveaux et les 333 relations d'auteur ou de collaborateur ; les autres candidatures Heurist restent hors visa.

## Effectifs

| Indicateur | Avant | Ajout du pilote | Après |
|---|---:|---:|---:|
| Autorités `PER` publiées | 242 | **80** | **322** |
| Contributions AdlFI | 1 980 | **0** | **1 980** |
| Notices AdlFI distinctes | 1 779 | **0** | **1 779** |
| Articles Gallia | 245 | **107** | **352** |
| Articles Gallia Préhistoire | 156 | **84** | **240** |
| Articles bibliographiques distincts | 401 | **191** | **592** |
| Relations « auteur » | 493 | **295** | **788** |
| Relations « collaborateur » | 85 | **38** | **123** |
| Relations bibliographiques | 578 | **333** | **911** |
| Autorités `PER` reliées au corpus bibliographique | 233 | **80** | **313** |

Les 333 relations du dossier de visa concernent 286 articles, dont **95 déjà publiés**, réutilisés sans copie, et **191 articles nouveaux**, ajoutés au catalogue.

Les nouvelles autorités reçoivent les identifiants **`PER-000243` à `PER-000322`**, avec `contributions_count: 0` : leurs activités bibliographiques ne sont jamais transformées en mentions AdlFI fictives. Les listes de contributions AdlFI (1 980) et de notices distinctes (1 779) restent inchangées.

## Contrôle de provenance et de parité

- **Archive privée visée :** `AdlFI_Heurist_Personnes_pilote80_v02_PRE_VISA.zip` ; SHA-256 `f0870ce800f700bdea6db58bb53ed52f36e7c308e454a9a93db7a8fa7816659e`.
- **Source Heurist :** `Export_Revue_Gallia_20261127115832.json` ; SHA-256 `de44407287e2f85132338119354924458320b2dd90cfd4ac30b8b4ee6c44c051`.
- **Empreinte canonique SHA-256 des 80 autorités publiées :** `0ab2d44606675e08ca31908449f21bda9ec00e9258850b70bb4dbe43ec738a9d`.
- **Empreinte canonique des 191 nouveaux articles :** `3c03609cd94de6816ec2dab6fecae9440ec056e947f27944f7b4d5e2770fc2bb`.
- **Empreinte canonique des 333 nouvelles relations :** `a5ca244539eeb0182fe6e4b7259da0f19fc8574ee6f32cc45227d439c4c0fde9`.
- Méthode d'empreinte canonique : `json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))`, puis SHA-256 des octets UTF-8.
- Le contrôle indépendant a confronté les **333 positions** des liens dans les champs bibliographiques de l'export source : aucune divergence, aucun doublon de triplet article–personne–rôle.
- Les PPN des 80 personnes ont été vérifiés modulo 11, sans collision avec les identifiants déjà publiés. Leurs formes et autres identifiants proviennent des autorités Heurist validées ; aucune identité n'a été déduite d'un rapprochement lexical.
- Les 242 autorités et 1 980 contributions AdlFI précédentes ainsi que les 401 articles et 578 relations bibliographiques antérieures ont été conservés à l'identique, dans le même ordre.
- Les concordances entre identifiants internes Heurist et identifiants `PER` restent **dans un fichier privé**, jamais dans les données publiques.

## Règles d'édition et limites documentaires

- Seuls les rôles publiables **`auteur`** et **`collaborateur`**, tels qu'attestés sur chaque article, sont conservés. Aucun lien relevant du processus interne de validation éditoriale ni donnée personnelle de contexte ne figure dans cette projection.
- Les 14 personnes possédant des formes alternatives conservent leurs variantes attestées avec le type neutre `autre_forme_attestee` ; aucune qualification maritale ou graphie IdRef n'est déduite.
- L'article `heurist:1519:73:4790`, « XIIe Circonscription [préhistorique] », *Gallia*, 1957, ne possède pas d'URL canonique dans la source : l'interface doit afficher sa référence **sans lien**.
- Parmi les 191 articles nouveaux, **28 DOI** sont absents ; une pagination est incomplète. Aucune valeur n'a été inventée et aucune URL HTTP n'a dû être normalisée dans ce lot.
- Les candidats non inclus dans les deux pilotes, notamment les identifiants partagés, les personnes sans PPN et l'auteur institutionnel, restent en instruction dans le dossier [#217](https://github.com/nicocoquet/adlfi-referentiels/issues/217). Aucun lot 09 AdlFI n'est créé.

## Fichiers et contrôles

- `docs/data/personnes.json` — ajout des 80 autorités ; schéma `0.5.0`.
- `docs/data/personnes-articles.json` — ajout des 191 articles et 333 relations ; schéma `0.1.0`.
- `docs/data/manifest.json` — effectifs des deux jeux de données synchronisés.
- `docs/index.html`, `docs/personnes/index.html` — périmètre et effectifs actualisés.
- `tests/test_personnes_heurist_pilote80_publication.py` — tests permanents de non-régression, comptage, identité, DOI/URL, confidentialité par liste blanche et rôles.
- `tests/test_personnes_articles_ui.js` — test d'interface des 322 autorités et 2 891 contributions toutes revues confondues, y compris les personnes sans notices AdlFI et les références sans URL.

**Réserve :** la réussite de la CI et la lecture du dépôt `main` ne remplacent pas une recette visuelle du site effectivement déployé. Ce contrôle reste suivi dans [l'issue #216](https://github.com/nicocoquet/adlfi-referentiels/issues/216).
