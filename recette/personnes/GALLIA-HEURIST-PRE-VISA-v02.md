# Personnes — Gallia / Gallia Préhistoire : recette documentaire v0.2 (pré-visa)

**État :** audit technique terminé ; **données candidates non validées et non publiées**.

**Source privée :** `Export_Revue_Gallia_20261127115832.json` (SHA-256 `de44407287e2f85132338119354924458320b2dd90cfd4ac30b8b4ee6c44c051`). Ne pas ajouter au dépôt cet export ni une matrice de visa nominative.

**Projection candidate privée :** `AdlFI_Gallia_pilote_v02_recette_pre_visa.zip` ; SHA-256 du JSON interne `d35d1fb7bf948df8e0fdbea6a59de65d8243ae3f1da9a76802de50f9079949b7`.

## Résultat de la confrontation

| Élément | Effectif |
|---|---:|
| Autorités `PER` rapprochées dans Heurist par IdRef | 202 |
| Autorités `PER` avec relations dans les deux revues | 193 |
| Articles bibliographiques candidats distincts | **337** |
| Articles `gallia` | 210 |
| Articles `gallia_prehistoire` | 127 |
| Relations candidates `auteur` | 424 |
| Relations candidates `collaborateur` | 49 |
| **Relations candidates totales** | **473** |

- Examen de la source Heurist : aucune divergence inexpliquée sur les titres, années, revues, volumes, pages, URL ou DOI des 337 articles retenus.
- Vérification des **473** relations : pointeurs personne–article, rôles bibliographiques (`dty_ID=15` / `1057`), positions à l'intérieur de chaque champ répétable : **0 divergence**.
- Rôles d'évaluation éditoriale et attributs de personnes non nécessaires : exclus par liste blanche de la projection et de la publication.
- Aucun DOI ni aucune URL dupliqués dans les 337 articles retenus ; aucun triplet article–personne–rôle dupliqué.
- Les contributions AdlFI déjà publiées ne sont pas modifiées.

## Anomalie bibliographique corrigée dans le candidat

Deux enregistrements Heurist distincts partageaient le même DOI et la même URL : `1392` et `872`, DOI `10.3406/galia.1998.3258`.

La notice de publication [Persée](https://www.persee.fr/doc/galia_0016-4119_1998_num_55_1_3258) atteste que **« L'environnement »** (enregistrement `1392`, p. 8-10) constitue une section de l'article **« L'occupation du site et son contexte environnemental »** (`872`, p. 8-18). L'autorité `PER-000171` était déjà reliée à l'article `872` comme auteur.

**Proposition de traitement dans la v0.2** : conserver l'article `872`, ne pas republier la section `1392` comme article distinct et ne pas compter deux fois la contribution correspondante. **La base source Heurist n'est pas modifiée.** Ce reclassement doit être visé explicitement avant publication des données.

Les tests permanents rejettent désormais tout nouveau doublon de DOI ou d'URL, **sans fusion automatique**.

## Réserves documentaires restant à traiter

- **6 URL OpenEdition** historiques converties de HTTP vers HTTPS ; l'enregistrement `41911` a été confronté à sa page en ligne, les cinq autres n'ont pas pu être confirmés indépendamment à cause du dispositif anti-robots. Elles ne sont pas déclarées invalides.
- **1 article sans URL ni DOI** dans l'extraction : Heurist `942`, titre « Modalités du démantèlement des lieux de culte et politique de grands travaux de l'Antiquité tardive à Narbo Martius », *Gallia*, 71-1 (2014), p. 65-77. Aucun lien canonique n'est inventé.
- **20 DOI absents** dans le corpus candidat (dont l'article précédent), **3 paginations incomplètes**. Une valeur manquante n'autorise pas une complétion conjecturale.
- Le contrôle de publication ne doit pas échouer du seul fait qu'OpenEdition active un contrôle anti-robots.

## Prochaine décision éditoriale

Valider la projection v0.2 (337 articles et 473 relations), y compris le reclassement du seul doublon identifié. Après visa seulement, produire `docs/data/personnes-articles.json` à statut `PUBLIC_PILOT` dans une PR de données séparée, avec CI et recette visuelle.

Le dépôt conserve ici uniquement le constat de recette et les empreintes des fichiers privés, **jamais** l'export Heurist brut ou les relations d'expertise.
