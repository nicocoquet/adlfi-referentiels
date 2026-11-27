# Personnes — publication du premier pilote de 40 autorités Heurist

**Visa éditorial :** 27 novembre 2026 (« ok valide »), portant expressément sur le dossier `AdlFI_Heurist_Personnes_pilote40_v01_PRE_VISA.zip`, ses 40 fiches et ses 105 relations aux articles.  
**Statut :** publication dans le référentiel commun aux revues AdlFI, Gallia et Gallia Préhistoire ; **aucun lot 09 AdlFI n'est ouvert**.

## 1. Périmètre du visa et effectifs

| Indicateur | Avant | Ajout | Après |
|---|---:|---:|---:|
| Autorités `PER` publiées | 202 | **40** | **242** |
| Contributions **AdlFI** | 1 980 | **0** | **1 980** |
| Notices AdlFI distinctes | 1 779 | **0** | **1 779** |
| Articles **Gallia** | 210 | **35** | **245** |
| Articles **Gallia Préhistoire** | 127 | **29** | **156** |
| Articles bibliographiques distincts | 337 | **64** | **401** |
| Relations « auteur » | 424 | **69** | **493** |
| Relations « collaborateur » | 49 | **36** | **85** |
| Relations bibliographiques | 473 | **105** | **578** |
| Autorités `PER` liées aux articles | 193 | **40** | **233** |

Le dossier visé comportait **90 articles distincts** liés aux 105 relations : **26 articles** appartenaient déjà au catalogue, **64 seulement** ont été ajoutés. Leur réutilisation évite toute duplication de notices bibliographiques.

Les 40 autorités validées reçoivent les identifiants **`PER-000203` à `PER-000242`**, avec `contributions_count: 0` : leurs contributions sont bibliographiques et ne doivent jamais accroître artificiellement les compteurs AdlFI. La concordance des IDs internes Heurist et des nouveaux `PER` est conservée **dans un fichier privé**, non dans les catalogues publics.

## 2. Provenance et preuve d'intégrité

- **Source Heurist privée** : `Export_Revue_Gallia_20261127115832.json`, SHA-256 `de44407287e2f85132338119354924458320b2dd90cfd4ac30b8b4ee6c44c051`.
- **Archive privée visée** : `AdlFI_Heurist_Personnes_pilote40_v01_PRE_VISA.zip`, SHA-256 `4ad67ae408dd54081d2a50e4a2f1094fd80d5c7b7ae4966c58dd93d587b4787c`.
- **Empreinte canonique SHA-256 des 40 nouvelles autorités** (JSON `ensure_ascii=False, sort_keys=True, separators=(',', ':')`) : `8003a010fe9cce041a87fd46a567f0d7c368b8c9389d2ba3261c15ed97f3e7dc`.
- **Empreinte canonique des 64 articles nouveaux** : `3b60b5cb30d5d135218a502f152399061b66c3435f87334ab48d453ce401e6dd`.
- **Empreinte canonique des 105 relations** : `a988081f2d4708459e24a9403a619dc88ae8e330d460a1a53eedcbcbc27fa8f3`.

Les matrices de visa de l'archive sont au statut historique `NON_RENSEIGNE` : ce statut documente **l'état avant décision humaine**, et n'est pas réécrit rétroactivement. Le visa a été donné séparément dans la conversation. La projection publique ne reprend ni les matrices, ni les notes internes, ni les identifiants de personnes Heurist.

Une confrontation indépendante, après visa, a relu dans l'export source les **40 noms et prénoms**, leurs alignements et variantes, les **64 titres nouveaux**, puis les **105 pointeurs personne–article, rôles et positions dans le champ répétable propre à chaque rôle** : zéro divergence après l'exclusion attendue de quatre valeurs non résolues `####` du champ Wikidata.

## 3. Règles d'édition et limites documentaires

- L'identité et les identifiants pérennes sont repris des fiches Heurist validées. **Aucune fusion nominative n'est inférée**.
- Cinq personnes possèdent des variantes de noms, dont quatre plusieurs variantes. Elles conservent le type neutre `autre_forme_attestee` et la source `Heurist`, sans déduire une forme maritale ou une forme canonique IdRef.
- Les 40 champs `name_idref` ne sont pas renseignés artificiellement.
- **Liste blanche positive et exclusive de relations de publication** : `auteur` et `collaborateur`. Aucun lien ou attribut relevant des procédures internes de validation éditoriale ne figure dans les catalogues ou dans le procès-verbal.
- Un des 64 nouveaux articles n'a ni URL ni DOI ; trois autres n'ont pas de DOI. Il est affiché sans lien arbitraire.
- Deux URL historiques d'OpenEdition ont été uniformisées en HTTPS dans le dossier préparatoire. Leur résolution effective reste à vérifier indépendamment, sans interpréter les protections anti-robots comme un échec.
- Les quatre valeurs `####` du champ Wikidata ont été exclues, sans créer d'alignement fictif.
- Les 202 autorités précédentes, les 1 980 contributions AdlFI, les 337 articles et 473 relations bibliographiques déjà publiés sont conservés sans modification.

## 4. Fichiers et contrôles

- `docs/data/personnes.json` : ajout de 40 autorités ; numéro de schéma `0.5.0` inchangé.
- `docs/data/personnes-articles.json` : ajout de 64 articles et 105 relations ; schéma `0.1.0` inchangé.
- `docs/data/manifest.json` : effectifs des deux catalogues corrigés et maintenus distincts.
- `docs/index.html`, `docs/personnes/index.html` : périmètre pilote et effectifs à jour.
- `tests/test_personnes_heurist_pilote40_publication.py` : cinq contrôles permanents (empreintes, identifiants, rôles et liens, statut, manifestes).
- `tests/test_personnes_articles_ui.js` : recette synthétique antérieure complétée par un chargement des **vraies données publiques** : 242 autorités et 2 558 contributions toutes revues confondues ; vérification d'une personne sans notice AdlFI et d'un article sans URL.

**L'interface et les données de publication sont un pilote non exhaustif.** Les 1 979 autres fiches du diagnostic à PPN non partagé, les quatre PPN ambigus, les cas sans PPN et l'auteur institutionnel restent à instruire, séparément.

## 5. Recette après fusion

La réussite de la CI attestera les tests Python / Node et la cohérence du catalogue déposé ; **elle n'est pas une preuve de recette visuelle réelle** sur GitHub Pages. Le contrôle visuel post-déploiement sera suivi dans [l'issue n° 216](https://github.com/nicocoquet/adlfi-referentiels/issues/216), qui devra être actualisée pour les 40 fiches supplémentaires avant clôture.
