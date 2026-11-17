# Reprise nationale — état des correspondances Pactols–COG en outre-mer

**17 novembre 2026 — PR 92. Inventaire des décisions déjà publiées, sans nouveau rapprochement.**

## Pourquoi ce bilan

Après le diagnostic géométrique approfondi de Hao (PR 80–91), les priorités reviennent à la **couverture documentaire nationale** : alignements d'autorités Pactols–COG, niveaux administratifs, histoire des codes. L'objectif n'est ni de poursuivre la comparaison de rasters pour une île particulière ni de déclarer validés des alignements encore absents.

**Source de vérité des validations en ligne :** `docs/data/lieux-outremer/recherche-2026.json`, contrôlée par `scripts/auditer_couverture_pactols_cog_outremer_2026.py`. Les décisions communales vérifiées dans les cinq registres éditoriaux de `recette/lieux/` recouvrent la Guadeloupe, la Martinique, la Guyane, La Réunion et la Polynésie.

## Couverture actuelle des identifiants communaux 2026

| Zone COG | Communes dans le moteur | Couples Pactols–COG validés | Sans lien validé |
| --- | ---: | ---: | ---: |
| 971 Guadeloupe | 32 | 32 | 0 |
| 972 Martinique | 34 | 34 | 0 |
| 973 Guyane | 22 | 22 | 0 |
| 974 La Réunion | 24 | 24 | 0 |
| 975 Saint-Pierre-et-Miquelon | 2 | 0 | 2 |
| 976 Mayotte | 17 | 16 | 1 |
| 987 Polynésie française | 48 | 48 | 0 |
| 988 Nouvelle-Calédonie | 33 | 0 | 33 |
| **Total** | **212** | **176** | **36** |

**Attention :** « sans lien validé » ne veut pas dire « sans concept Pactols ». Les **160 décisions** conservées dans les cinq registres éditoriaux sont contrôlées ligne par ligne contre l'index public ; les **16 liens Mayotte** sont contrôlés ici dans l'index, sans présumer qu'un registre homologue aux cinq autres existe dans `recette/lieux/`.

S'y ajoutent **4 validations distinctes d'autorités de collectivité** : `977` Saint-Barthélemy, `978` Saint-Martin, `986` Wallis-et-Futuna, `987` Polynésie française. Ces liens `collectiviteDOutreMer` ne sont **pas** des liens de communes et ne doivent pas être additionnés aux 176.

## Prochains lots territoriaux

### Priorité 1 — Nouvelle-Calédonie : 33 communes (988)

L'[audit historique COG](NOUVELLE-CALEDONIE-COG-HISTORIQUE-2026-RECETTE.md) fournit déjà le socle : 33 communes, dont **Kouaoua (98833)** issue d'une division de Canala en **1995**, et **Poya (98827)** répartie entre deux provinces. La construction du socle COG et l'instruction des provinces/aires coutumières **ne valent pas qualification Pactols**.

**Action suivante** : un audit du RDF Pactols Lieux `th17` du 22 juillet 2026, à commit et SHA-256 épinglés, sur les **33 codes actuels** `988xx`. Extraire pour chacun les `skos:exactMatch` vers `id.insee.fr/geo/commune/{code}`, l'ARK, le libellé français, les remplacements, les dépréciations et toutes les URI INSEE concurrentes. Classer en `ELIGIBLE_SELON_REGLE`, `A_INSTRUIRE`, `SANS_ASSERTION_EXPLICITE`, en distinguant les noms d'îles et d'aires coutumières des communes. **Ne rien valider avant d'avoir les résultats vérifiés**.

Cette tranche pourrait accroître fortement la couverture communale à coût de vérification limité : elle reprend les parseurs RDF et les règles déjà éprouvées en Guyane, Martinique, Guadeloupe et Réunion.

### Priorité 2 — Saint-Pierre-et-Miquelon : deux décisions

L'[audit Pactols/COG](SAINT-PIERRE-MIQUELON-PACTOLS-2026-RECETTE.md) a retrouvé des `exactMatch` pour les deux codes, sans publication :

- `97501` **Miquelon-Langlade** : ARK `26678/pcrtQAMzeGHldU` ; candidat **éligible**, sous réserve d'une décision éditoriale enregistrée.
- `97502` **Saint-Pierre** : le concept Pactols `26678/pcrtYQmFfwxLq8` porte le prefLabel **« île Saint-Pierre (Saint-Pierre-et-Miquelon) »** ; **ambiguïté de catégorie**, car la commune administrative ne se confond pas d'emblée avec l'île.

**Ne pas fusionner automatiquement ces deux dossiers** et ne pas valider `97502` sur le seul `exactMatch` malgré son existence explicite.

### Priorité 3 — Mayotte : Dembeni

La ligne `97607` possède un **ARK confirmé par l'éditeur** : `26678/crtZcuFSJVYZU`, conservé dans `ark_confirmes_non_valides`. Ce n'est **pas** un couple `skos:exactMatch` contrôlé et validé au titre du registre public : son statut doit être instruit séparément. Les **16 autres communes** ont un alignement déjà publié.

### Périmètres qu'il ne faut pas mélanger

Les **98 communes associées ISPF** de Polynésie ne sont pas de nouvelles communes COG à cinq chiffres. Les trois circonscriptions `98611`, `98612`, `98613` de Wallis-et-Futuna sont des **CIR** ; les quatre liens de collectivité ne doivent pas être transposés sur ces niveaux. En Nouvelle-Calédonie, les trois provinces et les huit aires coutumières relèvent d'autres types d'autorités. Les **anciennes communes** de Guadeloupe (`97123`, `97127`) ne doivent pas hériter des ARK des collectivités `977` et `978` par simple succession juridique.

L'[instruction Pactols–COG](POLITIQUE-ALIGNEMENT-PACTOLS-COG.md) reste la règle : validation **sur un millésime précis** d'un `skos:exactMatch` typé, univoque, non déprécié, à libellé compatible. Les géométries et leur validité historique font l'objet de contrôles indépendants.

## Production et non-régression

```bash
python3 -m unittest discover -s tests -p 'test_auditer_couverture_pactols_cog_outremer_2026.py' -v
python3 scripts/auditer_couverture_pactols_cog_outremer_2026.py \
  --index docs/data/lieux-outremer/recherche-2026.json \
  --registres recette/lieux \
  --sortie /tmp/adlfi-couverture-outremer-2026.json
```

Le workflow `lieux-couverture-pactols-cog-2026.yml` exécute le rapport deux fois et compare les résultats octet par octet ; artefact de recette hors `docs/`.

**Aucune nouvelle équivalence, aucun contour, aucune autorité et aucun ARK publiés par la PR 92.** L'extension métropolitaine sera abordée après le triage de ces 36 communes sans lien validé, en repartant du corpus de **9 928 autorités** et des candidatures Pactols–COG historiquement préparées.
