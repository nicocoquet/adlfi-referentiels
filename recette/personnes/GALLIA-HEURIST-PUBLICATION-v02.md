# Référentiel Personnes — publication du pilote Gallia / Gallia Préhistoire v0.2

**Visa éditorial obtenu :** conversation du 27 novembre 2026 (« c'est validé, on continue »), portant sur le candidat v0.2 audité et le traitement de l'exception documentaire.

**Statut :** publication du premier ensemble d'articles rattachés aux autorités `PER` déjà existantes. Ce pilote est **non exhaustif** ; il n'entraîne pas la création de nouvelles autorités Heurist.

## Périmètre

| Élément | Effectif |
|---|---:|
| Autorités PER publiées dans le catalogue principal | 202 |
| Autorités PER concernées par les articles du pilote | 193 |
| Articles Gallia | 210 |
| Articles Gallia Préhistoire | 127 |
| Articles bibliographiques distincts | **337** |
| Relations « auteur » | 424 |
| Relations « collaborateur » | 49 |
| Relations bibliographiques publiées | **473** |

La source relationnelle est une base Heurist validée par l'équipe éditoriale ; les relations portent **le rôle enregistré sur chaque article**, et non un statut global de la personne.

## Identité des sources et transformations

- Archive de recette privée : `AdlFI_Gallia_pilote_v02_recette_pre_visa.zip` (non déposée dans le dépôt Git).
- JSON candidat source (`personnes-articles_v02_CANDIDAT_NON_VALIDE.json`) : SHA-256 `d35d1fb7bf948df8e0fdbea6a59de65d8243ae3f1da9a76802de50f9079949b7`.
- Export Heurist original privé : `Export_Revue_Gallia_20261127115832.json` ; SHA-256 `de44407287e2f85132338119354924458320b2dd90cfd4ac30b8b4ee6c44c051`.
- Projection publiée (`docs/data/personnes-articles.json`) : SHA-256 `5c692c3dc947accd37ddf055044d92996102be9b4e91b8062997ec9c71809738`.
- **Transformations effectuées après visa : uniquement** `publication_status` de `CANDIDAT_NON_VALIDE` à `PUBLIC_PILOT` et reformulation de la note `scope_note` au présent. Les **337 objets article** et **473 objets contribution** ont été transférés sans modification des valeurs, de l'ordre ou des champs.
- Aucun champ personnel interne de Heurist ni lien rattaché à un processus éditorial confidentiel n'entre dans ce catalogue. Seuls les deux rôles publics « auteur » et « collaborateur » sont modélisés.

## Exception documentaire confirmée

Les enregistrements Heurist `1392` et `872` partagent le DOI `10.3406/galia.1998.3258`. Le premier décrit une section de l'article principal, non un article bibliographique autonome. Le visa v0.2 conserve **uniquement** `heurist:1519:73:872` dans le catalogue et ne comptabilise pas deux fois la contribution. La source Heurist n'a pas été modifiée.

## Réserves de qualité préservées

- Six URL historiques d'OpenEdition ont été uniformisées en HTTPS lors de la préparation privée ; cinq destinations n'ont pas pu être confirmées automatiquement (filtrage anti-robots). **Aucune résolution externe non contrôlée n'a été inventée.**
- L'article `heurist:1519:73:942` ne possède ni URL canonique ni DOI dans la source : l'interface l'affiche **sans lien hypertexte**, mais avec sa référence.
- Vingt DOI absents ; trois paginations incomplètes ; ces lacunes ne sont pas comblées par conjecture.
- Le référentiel AdlFI `docs/data/personnes.json` et ses compteurs (202 autorités, 1 980 contributions, 1 779 notices) sont conservés sans changement.

## Mise en œuvre

- Données : `docs/data/personnes-articles.json`, selon `docs/schemas/personnes-articles.schema.json` version `0.1.0`.
- Manifeste : `docs/data/manifest.json`, avec compteurs du module bibliographique séparés.
- Interface : `docs/personnes/index.html` et `docs/index.html` mis à jour pour refléter les relations effectivement publiées, sans prétention d'exhaustivité.
- Tests : `tests/test_personnes_articles_gallia.py` (intégrité de la projection, unicité DOI/URL, rôles, ponts d'autorités, manifeste) et `tests/test_personnes_articles_ui.js` (facettes et liens, rejet des données non validées).

## Réserves post-publication

La réussite de la CI vérifie la cohérence technique mais ne remplace pas un contrôle visuel effectif dans un navigateur. Les URLs historiques non confirmées restent des points de suivi documentaire. L'entrée `docs/data/personnes-articles.json` ne doit pas être confondue avec un index exhaustif des trois revues.

**Poursuite envisagée :** étendre le raccordement des articles et créer progressivement les nouvelles autorités Personnes Heurist, après vérification des collisions d'identifiants et sans réouvrir les lots AdlFI clos.
