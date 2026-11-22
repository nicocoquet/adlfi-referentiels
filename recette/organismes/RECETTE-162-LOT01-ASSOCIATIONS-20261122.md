# Recette Organismes 1.62 — lot 01 : huit associations

Date : 22 novembre 2026. **État : candidat, non fusionné.**

## Provenance

| Élément | Version 1.61 | Candidat 1.62 |
|---|---|---|
| XLSX maître | `AdlFI_referentiel_1-61_lot01_activites_et_date_CANDIDAT.xlsx` | `AdlFI_referentiel_1-62_lot01_huit_associations_CANDIDAT.xlsx` |
| SHA-256 | `fb475d0270ca74757c7d34dc97978897dccdf5b12cc10c2ec8aa3f35a65e8b98` | `430cef30bd9aa2cd0a70e2b6c384f9cbc91cc7aca4e8d70b53de7a666645cc52` |
| Git public | `f319a8a0e0a2187656ff5f1bf7758fe30c4e05e3` | PR 1.62 en brouillon |

Le XLSX candidat conserve les **41 membres OOXML** du maître, dont **un seul diffère** : `xl/worksheets/sheet2.xml` (Organismes). Une comparaison indépendante des cellules établit **exactement huit additions de valeurs**, les autres cellules et les autres éléments XML demeurant inchangés.

## Décisions documentaires

Les huit décisions ciblent exclusivement le champ `actif` : passage du vide à `oui`.

| ID | Cellule | Source indicative et décision documentaire |
|---|---|---|
| ORG-0176 — Société de recherche archéologique d'Alsace Bossue | L168 | [Conférence de janvier 2026](https://www.dna.fr/culture-loisirs/2026/01/12/le-site-archeologique-du-gurtelbach-a-dehlingen-au-coeur-d-une-conference) |
| ORG-0231 — Groupe de recherche en archéologie navale | L223 | [Compte rendu associatif, campagne de 2026](https://archeonavale.org/gran-languedoc-campagne-grau-de-melgueil-2026/) |
| ORG-0321 — Association Montagne et Patrimoine | L313 | [Exposition de l'été 2026](https://www.amont-alpesmaritimes.fr/activites/exposition-2026-la-madone-de-fenestres.html) |
| ORG-0341 — Anao, l'aventure sous-marine | L332 | [Forum des associations de septembre 2026](https://www.clubanao.org/forum-des-associations-ee-beaulieu-sur-mer-succes-garanti-pour-anao/) |
| ORG-0422 — Comité départemental de spéléologie et de canyon des Alpes-Maritimes | L410 | [Manifestation d'août 2026](https://scenesdusud.fr/spectacle/nuit-de-la-chauve-souris-valbonne) |
| ORG-0496 — Les Amis du Mez | L481 | [Catalogue REMPART 2026](https://catalogue.rempart.com/patrimoine/chateau/) |
| ORG-0524 — Société d'archéologie et de mémoire maritime | L509 | [Actualités associatives 2026](https://archeosousmarine.net/) |
| ORG-0525 — Société des sciences naturelles, archéologiques et historiques de la Creuse | L510 | [Séances publiques de septembre et novembre 2026](https://www.jds.fr/gueret/spectacles/seance-de-communications-1733077_A) |

Les mentions **GRAN, AMONT, SAMM** dans le registre sont des sigles d'usage et ne remplacent pas les noms retenus dans le maître.

## Réserves non modifiées

- **ORG-0212 — Société archéologique de Bron** : présence en 2025 attestée, pas d'activité propre datée pour 2026 dans le dossier.
- **ORG-0342 — Fédération monégasque des activités subaquatiques** : existence dans l'annuaire fédéral, mais pas d'activité propre récente suffisamment établie.
- **ORG-0355 — Équipe d'explorations spéléologiques de Villefranche** : annuaire fédéral seulement.
- **ORG-0341 — Anao** : incohérence possible entre l'année 1987 du maître et la création RNA en 2001 ; aucune modification de date à ce stade.
- **ORG-0524 — SAMM** : création indiquée en 1993 par le site associatif, mais date juridique non consolidée.
- Aucune nouvelle relation, autorité, date ni qualification de validation institutionnelle.

## Contrôle JSON strict

La branche contient une **projection déterministe** du JSON public 1.61, recalculée uniquement selon les règles de l'exporteur officiel : `activity.active=true` et `quality.activity_unknown=false` pour les huit autorités, plus deux champs de provenance. La recette `tests/test_recette_publication_organismes_162.py` doit constater **18 différences de valeurs exactement**.

Invariants : **935 autorités** (735 ORG et 200 SER), **683 incluses**, **252 exclues**, **600 relations**, **727 actives**, **142 inactives**, **66 indéterminées**.

## Vérification bloquante avant fusion

La projection du JSON doit encore être comparée **bit à bit** à une génération officielle depuis ce maître exact. Sur la branche 1.62, depuis la racine du dépôt :

```bash
MASTER="$HOME/Downloads/AdlFI_referentiel_1-62_lot01_huit_associations_CANDIDAT.xlsx"
shasum -a 256 "$MASTER"
SOURCE_DATE_EPOCH=1795305600 python3 scripts/export_organismes.py "$MASTER"
git diff --exit-code -- docs/data/organismes.json
```

Le SHA doit être `430cef30bd9aa2cd0a70e2b6c384f9cbc91cc7aca4e8d70b53de7a666645cc52`. La dernière commande doit retourner 0 sans différence. En cas d'écart, enquêter et corriger les données, jamais assouplir les assertions différentielles.

CI Python, Node et Chromium obligatoire. Tant que la parité officielle n'est pas consignée, **ne pas fusionner**.
