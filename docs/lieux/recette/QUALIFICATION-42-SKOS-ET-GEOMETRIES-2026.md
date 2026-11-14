# Lieux — Qualification SKOS et géométries contemporaines : recette nationale

**État : instruction technique non validante, sans modification du module Lieux public.**

## 1. Les 42 exceptions au contrôle SKOS Pactols

La source est l'artefact `controle_concepts_pactols.csv` du contrôle du RDF
`Pactols_Lieux_th17_20260722.rdf` de Frantiq. La présence des 9 928 ARK dans
cet export daté est déjà démontrée par le workflow de recette.

Le script `scripts/qualifier_exceptions_skos_lieux.py` produit une table de
**42 exceptions** (`qualifications-skos-exceptions-42.csv`) et le rapport
`rapport-qualifications-skos-42.json`. Le classement est exclusif :

| Catégorie | Nombre | Conséquence éditoriale |
| --- | ---: | --- |
| Ancienne abréviation hydrographique/physique | 26 | Conserver la forme XML et préférer le `prefLabel` daté pour affichage, sans changer l'ARK |
| Variante `skos:altLabel` attestée | 9 | Conserver l'ARK, les deux formes et leur provenance ; la variante n'atteste pas sa période historique |
| Distinction administrative historique ou typologique | 6 | Séparer les épisodes COG, les anciennes communes, les communes déléguées et l'île Saint-Pierre |
| Concept déclaré déprécié | 1 | Oisans Massif : conserver l'attestation et demander une vérification à Frantiq avant toute substitution |

**Alerte :** l'`altLabel` numérique `08140` du concept **Bazeilles** ne peut
pas être utilisé comme code INSEE de Bazeilles : le COG 2026 attribue le code
`08053` à Bazeilles et `08140` à Dom-le-Mesnil. Signaler cette valeur,
**sans corriger le thésaurus ni fabriquer d'`exactMatch`**.

Le résultat national est construit depuis le CSV de l'audit et non depuis la
seule transcription du bilan Markdown. La source et le RDF original sont
tracés par leurs empreintes SHA-256.

Commande de reproduction après téléchargement de l'artefact GitHub Actions :

```bash
python3 scripts/qualifier_exceptions_skos_lieux.py \
  --controle-skos /chemin/vers/controle_concepts_pactols.csv \
  --sortie /chemin/vers/recette-skos
```

## 2. Première connexion aux géométries data.gouv.fr : 30 propositions

Le script `scripts/auditer_raccordements_geometriques_2026.py` reçoit les
**30 couples proposés des sous-lots 01–03**, puis vérifie l'existence du code
COG dans le GeoJSON `communes-100m` **millésime 2026**.

**Il ne produit ni une correspondance Pactols–COG validée, ni une géométrie
historique.** Le lien est déclaré `non_valide` même lorsque le code et le nom
sont présents dans le GeoJSON. Il détecte séparément un code absent et un code
présent dont le libellé est divergent. Il protège contre les géométries
non polygonales, les codes dupliqués et une modification du millésime
sans modification explicite du contrat.

Source : [Contours administratifs, data.gouv.fr](https://www.data.gouv.fr/datasets/contours-administratifs),
répertoire 2026 :
https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2026/geojson/

Provenance à préserver : URL, producteur, licence **ODbL-1.0**, millésime,
généralisation, empreinte SHA-256 du fichier téléchargé, nom et code COG.
Les données sont des contours *contemporains généralisés* ; aucune validité
sur une époque archéologique n'est déduite.

Le workflow `.github/workflows/audit-geometries-lieux-cog2026.yml` doit
réaliser le contrôle sans intervention sur le Mac de l'éditeur. Il génère
un **artefact de recette**, contenant :

- `rapport-raccordement-geometries-2026.json` : bilan des 30 couples,
  comptes des contours présents/absents et SHA-256 de la source ;
- `raccordements-candidats-cog2026.json` : une proposition par ARK,
  avec son code, sa géométrie 2026 éventuelle et un statut **non validé** ;
- `contours-candidats-cog2026.geojson` : contours extraits, non publiés.

La source communale de référence du pilote PACA demeure
`docs/data/lieux-communes.geojson` (généralisation **1 000 m**) : ne pas
mélanger silencieusement les contours `100m` avec ce jeu pour une
visualisation commune. Une recette cartographique devra fixer une même
résolution par couche ou comparer les contours source par source et
mettre en évidence leurs différences. Pour les arrondissements municipaux,
conserver les règles de géométrie distincte et les raccordements déjà
étudiés dans la PR n°23.

### Modèle d'identité à préserver

- **ARK** : concept Pactols, labels et variantes datés par la source SKOS.
- **Épisode administratif** : `TYPECOM`, `COM`, libellé et intervalle
  provenant de l'Insee, plus mouvements ; code invariant ≠ entité temporelle
  nécessairement identique.
- **Géométrie** : produit, millésime, généralisation, empreinte et statut
  d'appariement. Un contour 2026 **ne remonte pas dans le temps**.
- **Relation d'alignement** : décision éditoriale explicite, avec preuve
  et provenance. Aucune candidature n'est publiée sans validation.

**État de publication inchangé : 103 couples PACA déjà validés.**
