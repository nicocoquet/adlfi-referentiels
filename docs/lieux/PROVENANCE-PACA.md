# Pilote Lieux AdlFI — PACA / Pactols–COG 2026

## Objet

Premier jeu de consultation du module **Lieux** pour le site Référentiels AdlFI.
L'unité principale est **l'autorité géographique Pactols**, identifiée par son ARK.
Un lien éditorial validé vers une commune COG 2026 permet de retrouver sa géométrie.
Le pilote ne publie **aucune équivalence SKOS inférée** : une correspondance validée
dans notre table éditoriale n'est pas automatiquement un `skos:exactMatch` de Pactols.

Ce lot contient uniquement les correspondances éditoriales PACA validées le
**18 octobre 2026**. Aucune commune n'est résolue par homonymie ou concordance
automatique de libellés.

## Livrables en recette

- `docs/data/lieux.json` : **103 autorités Pactols** et **103 correspondances
  COG validées**, avec statut éditorial, date, source et millésime 2026.
- `docs/data/lieux-communes.geojson` : **103 géométries** sélectionnées
  exclusivement au moyen des codes INSEE validés. Il s'agit de contours du
  fichier cartographique de l'atlas, **pas de contours historiques**.
- `scripts/export_lieux_paca.py` : producteur déterministe en lecture seule.
  Il vérifie le contenu des sources par leur SHA-1 Git et refuse toute divergence.
- `tests/test_export_lieux_paca.py` : invariants métier, contrôles de provenance
  et tests négatifs.

**La présence des fichiers sur une branche de travail ne signifie pas
publication en ligne** : seule la branche principale alimente GitHub Pages.
La page `docs/lieux/index.html` et le manifeste ne sont pas modifiés dans ce lot.

## Corpus et exclusions

| Statut dans la table éditoriale | Nombre | Traitement |
| --- | ---: | --- |
| `VALIDE_EDITEUR_2026_10_18` | 103 | Exporté |
| `REVU_EDITEUR_A_DOCUMENTER` | 110 | Non exporté |
| `HORS_COG_CONFIRME` | 3 | Non exporté dans le pilote communal |
| `A_COMPLETER_SOURCE` | 2 | Non exporté |
| **Total** | **218** | **103 fiches publiables** |

Le fichier géométrique source comporte **106 entités**.
Les 103 correspondances validées ont chacune une géométrie et un code distinct.
Les trois géométries supplémentaires sont celles de **Nice (06088),
Marseille (13055) et Hyères (83069)** ; elles ne sont pas exportées ici.
Leur exclusion ne signifie pas que ces villes n'existent pas dans le COG :
**c'est leur alignement éditorial Pactols–COG qui reste à instruire**.

## Sources figées

Les données sources ont été lues dans le dépôt privé
`nicocoquet/atlas-documentaire`, branche
`feat/referentiel-pactols-cog-2026`, commit
`bc0455c7d1dbf65f579e9b25a01eb7928a8054d5`.

| Source | Chemin source | SHA du blob Git |
| --- | --- | --- |
| Table éditoriale | `experimentation/donnees/autorite_pactols_insee.csv` | `8d039fe574413df89524b39540ba962ce89ca0a0` |
| Géométries | `cartographie/geometries/communes-1000m.geojson` | `0525607f277ec4c915a3e3273e716a5b1f1108d5` |

Les fichiers éditoriaux non filtrés **ne sont pas copiés** dans le dépôt public.
Leurs empreintes sont consignées afin de pouvoir reproduire l'export sans
dépendre de l'état ultérieur des branches. Le référentiel historique COG
national dispose de scripts distincts et n'est pas intégré par cette livraison.

## Regénérer sans publier

Depuis la racine de `adlfi-referentiels`, en ayant accès aux deux fichiers
sources au commit indiqué :

```bash
SORTIE="$(mktemp -d "${TMPDIR:-/tmp}adlfi-lieux-recette.XXXXXX")"

python3 scripts/export_lieux_paca.py \
  /chemin/vers/autorite_pactols_insee.csv \
  /chemin/vers/communes-1000m.geojson \
  --output-dir "$SORTIE"

python3 -m unittest discover -s tests -v
```

L'exporteur bloque si une source a été modifiée, même de manière
apparemment anodine. Il refuse notamment les nouveaux codes non validés,
les doublons d'ARK/code, une géométrie absente ou une autre région.

L'option `--output-dir` est obligatoire et l'écriture directe dans
`docs/data` est interdite par le script pendant cette recette.

## Contrat de données provisoire (`schema_version: 0.1.0`)

Une autorité contient :

- `ark_pactols` et `libelle_pactols` : identité documentaire ;
- `type_entite` : `commune` dans ce seul pilote ;
- `correspondances[]` : relation éditoriale validée vers un code INSEE,
  libellé COG, millésime, département et provenance de la validation.

Le tableau `correspondances[]` est volontairement extensible à plusieurs
relations futures ; la cardinalité **1:1** du pilote n'est pas une règle
ontologique générale.

Le GeoJSON inclut le code INSEE et l'ARK Pactols correspondant pour permettre
la sélection cartographique. Les variantes de noms Pactols (`altLabel`)
ne figurent pas dans la table éditoriale de cette version : elles devront
être enrichies à partir d'un export SKOS Pactols contrôlé, **sans être inventées**.

## Conditions préalables à la mise en ligne

1. Relire les fiches et les 103 correspondances générées.
2. Vérifier l'attribution et les conditions de réutilisation de la source
   géométrique avant une publication durable.
3. Définir la page cartographique et son comportement en cas de lieux
   sans géométrie, de codes historiques et de relations non bijectives.
4. Fusionner une PR validée seulement après tests et recette visuelle.
